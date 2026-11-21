import os
import re

from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    CHROME_BASE,
    CHROME_DEEP,
    DARK_BUNDLE,
    DARK_MUTED_TIER,
    DARK_BUNDLE_FORBIDDEN_PURPLE,
    WCAG_AA_NORMAL_TEXT,
    _VAR_RE,
    _contrast_ratio,
    _iter_rules,
    _normalize_colour,
    _winning_declaration,
)
from odoo.addons.viin_brand.tests.test_brand_ssot import (
    BRAND_VARIABLES_SCSS,
    _resolve_scss_hex,
)

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BACKEND_BUNDLE = "web.assets_backend"

# Element ancestor pools (class-only) from home_menu.xml: `.o_viin_home_menu` >
# `.o_viin_home_content` > `.o_viin_home_body` > `.o_viin_home_section_label`. The menu root is
# modelled separately because it declares the page band the label renders on
# (`background-color: var(--secondary-bg)`).
HOME_MENU_ROOT_CLASSES = frozenset({"o_viin_home_menu"})
HOME_MENU_ROOT_ANCESTORS = frozenset({"o_web_client", "o_action_manager"})
HOME_SECTION_LABEL_CLASSES = frozenset({"o_viin_home_section_label"})
HOME_SECTION_LABEL_ANCESTORS = HOME_MENU_ROOT_ANCESTORS | HOME_MENU_ROOT_CLASSES | {
    "o_viin_home_content", "o_viin_home_body", "d-flex", "flex-column", "flex-grow-1",
}
# The muted-grey token the label takes in the dark bundle; named so failure messages can say what
# the default is.
DEFAULT_LABEL_TOKEN = "--secondary-color"


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_scss_comments(text):
    """Drop // line and /* */ block comments so a rule is never matched inside a comment."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _root_prop(css, name):
    """Read a custom property declared on a ``:root`` rule.

    The class-based cascade resolver does not model ``:root``, so a ``color`` that resolves through
    a ``:root`` custom property is read here.

    :return: the last value declared for ``name`` (source order wins), or ``None``
    """
    values = []
    for _order, selector, body in _iter_rules(css):
        if selector.strip() != ":root":
            continue
        for declaration in body.split(";"):
            key, separator, value = declaration.partition(":")
            if separator and key.strip() == name:
                values.append(value.strip())
    return values[-1] if values else None


def _resolve_to_hex(css, value):
    """Normalise ``value`` to a ``#rrggbb`` colour, following one ``var()`` hop through ``:root``.

    Accepts both a literal (``color: #4fd4e2``) and a runtime property (``color: var(--link-color)``).

    :return: the hex colour, or ``None`` when ``value`` is empty or carries no colour
    """
    if value is None:
        return None
    match = _VAR_RE.match(value.strip())
    if match:
        resolved = _root_prop(css, match.group(1))
        value = resolved if resolved is not None else match.group(2)
    return _normalize_colour(value) if value else None


@tagged("post_install", "-at_install")
class TestThemeDarkWidgetContrast(TransactionCase):
    """The theme's own widget surfaces are readable in both compiled bundles.

    Dark mode is the recompiled ``web.assets_web_dark`` bundle (dark_palette.scss of viin_brand), so
    these guards read the value a real element computes through the compiled cascade, reusing the
    cascade and WCAG helpers of viin_brand.
    """

    def _compiled_css(self, bundle_name):
        """Compile ``bundle_name`` and return its CSS payload as decoded text."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so its surfaces cannot be "
            "verified." % bundle_name,
        )
        return css

    def test_backend_bundle_compiles_to_a_healthy_stylesheet(self):
        """web.assets_backend compiles to a large, error-free stylesheet.

        A Sass compile abort (e.g. a var()-ified surface variable feeding color-contrast()) collapses
        the bundle to a small stub carrying the "A css error occured" banner and leaves the webclient
        unstyled.
        """
        css = self._compiled_css(BACKEND_BUNDLE)
        self.assertGreater(
            len(css), 100_000,
            "web.assets_backend compiled to only %d bytes - the SCSS build aborted (a var()-ified "
            "surface var / color-contrast() landmine, or another Sass error). The webclient would "
            "render unstyled." % len(css),
        )
        self.assertNotIn(
            "a css error occured", css.lower(),
            "web.assets_backend carries the Odoo CSS-error banner - the bundle did not compile clean.",
        )

    def test_home_menu_section_label_is_the_structure_purple_on_its_own_band(self):
        """The home-menu section label is the structure purple in light, and readable in both schemes.

        The brand colour law reads teal = act, purple = meta-structure. "Applications" organises the
        app grid, so in LIGHT mode it is the purple ``$o-brand-secondary`` accent, never a teal. In
        DARK mode it is not purple: it is ``var(--secondary-color)``, which flips dark-correct on its
        own through the ``$body-secondary-color`` of dark_palette.scss. The choice is made at compile
        time by the ``$o-viin-dark-bundle`` flag, so each bundle carries exactly one ``color``
        declaration and there is no dark companion file.

        The contrast is measured against the band the compiled bundle declares for the menu root in
        that bundle, not a hardcoded page colour.
        """
        expected_purple = _resolve_scss_hex(_read(BRAND_VARIABLES_SCSS), "$o-brand-secondary")
        self.assertIsNotNone(
            expected_purple,
            "$o-brand-secondary must be declared in viin_brand's brand_variables.scss - it "
            "is the SSOT for every META/STRUCTURE purple surface in this cluster.",
        )
        expected_purple = expected_purple.lower()

        label = {
            "classes": HOME_SECTION_LABEL_CLASSES,
            "ancestors": HOME_SECTION_LABEL_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        menu_root = {
            "classes": HOME_MENU_ROOT_CLASSES,
            "ancestors": HOME_MENU_ROOT_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)

            raw_label = _winning_declaration(css, label, ("color",))
            self.assertIsNotNone(
                raw_label,
                "No compiled `color` applies to .o_viin_home_section_label in %s - the home-menu "
                "SCSS is not reaching that bundle." % bundle_name,
            )
            colour = _resolve_to_hex(css, raw_label)
            self.assertIsNotNone(
                colour,
                "The %s home-menu section label `color` %r carries no resolvable colour."
                % (arm, raw_label),
            )
            self.assertNotIn(
                colour, (CHROME_BASE, CHROME_DEEP),
                "The %s home-menu section label compiled the teal %s. A section label is "
                "STRUCTURE, not an ACT - see the colour law in viin_brand's "
                "brand_variables.scss." % (arm, colour),
            )
            if arm == "light":
                self.assertEqual(
                    colour, expected_purple,
                    "The home-menu section label compiled %s instead of the brand secondary %s "
                    "($o-brand-secondary). A revert to the muted `var(%s)` grey looks like this."
                    % (colour, expected_purple, DEFAULT_LABEL_TOKEN),
                )
            else:
                self.assertNotEqual(
                    colour, expected_purple,
                    "The home-menu section label compiled the light brand purple %s in the DARK "
                    "bundle, which is unreadable on the dark band. The purple accent is light-only; "
                    "wrap the declaration in `@if not $o-viin-dark-bundle`."
                    % expected_purple,
                )
                self.assertNotEqual(
                    colour, DARK_BUNDLE_FORBIDDEN_PURPLE,
                    "The home-menu section label compiled the dark-tuned purple %s. A darker purple is "
                    "not the answer to the dark canvas - the answer is no purple."
                    % DARK_BUNDLE_FORBIDDEN_PURPLE,
                )
                self.assertEqual(
                    colour, DARK_MUTED_TIER,
                    "The home-menu section label compiled %s in the dark bundle instead of the "
                    "muted tier %s that `var(%s)` resolves to there. That token IS the default "
                    "look the label falls back to in dark; anything else means a dark "
                    "accent of ours is still being emitted."
                    % (colour, DARK_MUTED_TIER, DEFAULT_LABEL_TOKEN),
                )

            raw_band = _winning_declaration(css, menu_root, ("background-color", "background"))
            self.assertIsNotNone(
                raw_band,
                "The .o_viin_home_menu root declares no background in %s, so the band the label "
                "renders on cannot be resolved." % bundle_name,
            )
            band = _resolve_to_hex(css, raw_band)
            self.assertIsNotNone(
                band,
                "The %s home-menu band %r carries no resolvable colour." % (arm, raw_band),
            )
            ratio = _contrast_ratio(colour, band)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "The home-menu section label renders %s on the %s band %s - %.2f:1, below the WCAG "
                "AA normal-text threshold of %.1f:1. In the dark bundle this is the signature of a "
                "$o-brand-secondary that lost its dark arm."
                % (colour, arm, band, ratio, WCAG_AA_NORMAL_TEXT),
            )


class TestThemeCompileSafetyInvariants(BaseCase):
    """Static source guards, with no database, for the two compile-abort landmines that leave the
    webclient unstyled or blank."""

    def test_surface_vars_are_never_var_ified(self):
        """primary_variables.scss never var()-ifies a surface variable that feeds a Sass colour function.

        ``$o-view-background-color`` and ``$o-webclient-background-color`` feed core's ``$body-bg``
        -> ``color-contrast()`` -> ``mix()``, which cannot evaluate a ``var()`` at compile time; a
        var()-ified one aborts the whole ``web.assets_web`` bundle. They stay real hexes: dark is
        delivered by the recompiled ``web.assets_web_dark`` bundle, not a runtime variable flip.
        """
        source = _strip_scss_comments(
            _read(os.path.join(MODULE_DIR, "static", "src", "scss", "primary_variables.scss"))
        )
        for var_name in ("$o-view-background-color", "$o-webclient-background-color"):
            offenders = re.findall(re.escape(var_name) + r"\s*:\s*[^;]*var\(", source)
            self.assertFalse(
                offenders,
                "%s is var()-ified in primary_variables.scss (%r). That poisons core's "
                "$body-bg -> color-contrast() -> mix() and aborts the whole web.assets_web bundle "
                "(unstyled webclient). Keep it a real hex." % (var_name, offenders),
            )

    def test_no_double_hyphen_in_xml_comments(self):
        """No XML comment under static/src contains '--' (double hyphen).

        '--' is illegal inside ``<!-- ... -->`` and makes the QWeb parser reject the whole
        web.assets template bundle, so ``Missing template "web.WebClient"`` blanks the entire
        backend.
        """
        static_src = os.path.join(MODULE_DIR, "static", "src")
        offenders = []
        for root, _dirs, files in os.walk(static_src):
            for name in files:
                if not name.endswith(".xml"):
                    continue
                path = os.path.join(root, name)
                for match in re.finditer(r"<!--(.*?)-->", _read(path), re.DOTALL):
                    if "--" in match.group(1):
                        offenders.append(
                            "%s: %r" % (os.path.relpath(path, MODULE_DIR), match.group(1).strip()[:70])
                        )
        self.assertFalse(
            offenders,
            "XML comment(s) contain an illegal '--' (double hyphen), which breaks the entire "
            "web.assets template bundle and blanks the webclient:\n%s" % "\n".join(offenders),
        )
