import os
import re

from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    DARK_BUNDLE,
    WCAG_AA_NORMAL_TEXT,
    _VAR_RE,
    _contrast_ratio,
    _iter_rules,
    _normalize_colour,
    _winning_declaration,
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
# The structural accent of the brand palette: purple in the light scheme, cyan in the dark one.
LIGHT_SECTION_LABEL = "#7f4282"
DARK_SECTION_LABEL = "#00bbce"


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

    def test_home_menu_section_label_is_the_structural_accent_and_readable_on_its_band(self):
        """The home-menu section label is the brand accent of each scheme, readable on its band.

        The structural accent is purple in the light scheme and cyan in the dark one. The
        contrast is measured against the band the compiled bundle declares for the menu root in
        that bundle, not a hardcoded page colour.
        """
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
        expected = {"light": LIGHT_SECTION_LABEL, "dark": DARK_SECTION_LABEL}
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)

            raw_label = _winning_declaration(css, label, ("color",))
            self.assertIsNotNone(
                raw_label,
                "No compiled `color` applies to .o_viin_home_section_label in %s - the home-menu "
                "SCSS is not reaching that bundle." % bundle_name,
            )
            colour = _resolve_to_hex(css, raw_label)
            self.assertEqual(
                colour, expected[arm],
                "The %s home-menu section label compiled %s instead of the brand accent %s."
                % (arm, colour, expected[arm]),
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
                "AA normal-text threshold of %.1f:1." % (colour, arm, band, ratio, WCAG_AA_NORMAL_TEXT),
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
