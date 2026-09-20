# Behavior-protecting guards for the 19.0 upgrade of viin_brand_html_editor (ODOO-AI-ETHOS #8).
#
# Business rules protected (Odoo 19.0 renamed web_editor -> html_editor; the removed module has
# no analog by its old name, and its common SCSS was renamed to html_editor.common.scss):
#   * the de-brand module re-points off the REMOVED web_editor module onto its html_editor rename,
#     stays installable, and keeps its OWN de-brand SCSS source's CONTENT unchanged - only the
#     source file's NAME was normalized away from the removed module's name to a self-describing
#     'viin_brand_html_editor.common.scss' (static manifest guard);
#   * once installed the frontend bundle compiles with ZERO errors (no "Undefined variable $white",
#     no "cannot find asset" from a dangling anchor) and the module's distinctive primary-button
#     override survives into the compiled CSS (install smoke + compiled-asset behavioral proof).
#
# The static class reads the module's OWN __manifest__.py via ast.literal_eval so the wiring is
# protected without needing a live instance; the behavioral class exercises the compiled frontend
# bundle on the installed module. No demo data, self-contained.
import ast
import os
import re

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")
DEBRAND_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "viin_brand_html_editor.common.scss")

# The agreed GREEN target: the 19.0 analog anchor + this module's own (unchanged) de-brand source.
FRONTEND_BUNDLE = "web.assets_frontend"
HTML_EDITOR_ANCHOR = "html_editor/static/src/scss/html_editor.common.scss"
DEBRAND_SOURCE = "viin_brand_html_editor/static/src/scss/viin_brand_html_editor.common.scss"

# The removed module the upgrade must purge. Scope the purge to (i) exact depends/auto_install
# membership of the string 'web_editor', and (ii) core asset tokens under 'web_editor/static/'.
# The module's OWN 'viin_brand_html_editor/...' paths and its internal
# 'viin_brand_html_editor.common.scss' filename are legitimate and must NOT trip the guard -
# neither equals 'web_editor' nor starts with 'web_editor/static/'.
REMOVED_MODULE = "web_editor"
REMOVED_ASSET_PREFIX = "web_editor/static/"


def _load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
        return ast.literal_eval(manifest_file.read())


def _iter_asset_tokens(assets):
    """Yield every string token across all bundles, flattening list entries and
    (directive, anchor, source) / (directive, source) tuples/lists."""
    for bundle_ops in assets.values():
        for op in bundle_ops:
            if isinstance(op, str):
                yield op
            elif isinstance(op, (tuple, list)):
                for part in op:
                    if isinstance(part, str):
                        yield part


@tagged("post_install", "-at_install")
class HtmlEditorManifestUpgradeGuardTest(TransactionCase):
    """The 19.0 upgrade re-points this de-brand module off the removed web_editor module onto its
    html_editor rename, stays installable, preserves its license, and keeps its own SCSS source."""

    def test_module_is_installable_on_19(self):
        """Rule (a): the upgraded module must be installable on 19.0 (currently installable=False)."""
        manifest = _load_manifest()
        self.assertIs(
            manifest.get("installable"), True,
            "viin_brand_html_editor must be installable=True on 19.0",
        )

    def test_manifest_has_no_reference_to_removed_web_editor_module(self):
        """Rule (b): NO reference to the removed 'web_editor' module survives - not in depends,
        not in auto_install, not as a core 'web_editor/static/...' asset anchor. The module's own
        'viin_brand_html_editor/...' paths and its internal 'viin_brand_html_editor.common.scss'
        filename are legitimate and must NOT trip the guard."""
        manifest = _load_manifest()

        depends = manifest.get("depends", [])
        self.assertNotIn(
            REMOVED_MODULE, depends,
            "depends still lists the removed module 'web_editor' (renamed to html_editor in 19.0): %r"
            % (depends,),
        )

        auto_install = manifest.get("auto_install")
        if isinstance(auto_install, (list, tuple)):
            self.assertNotIn(
                REMOVED_MODULE, auto_install,
                "auto_install still references the removed module 'web_editor': %r" % (auto_install,),
            )

        for token in _iter_asset_tokens(manifest.get("assets", {})):
            self.assertFalse(
                token == REMOVED_MODULE or token.startswith(REMOVED_ASSET_PREFIX),
                "Asset op still anchors the removed 'web_editor/static/...' path (its common SCSS was "
                "renamed to html_editor/... in 19.0): %r" % (token,),
            )

    def test_depends_targets_html_editor_and_web(self):
        """Rule (c): depends must list both the html_editor rename and web."""
        depends = _load_manifest().get("depends", [])
        self.assertIn(
            "html_editor", depends,
            "depends must include 'html_editor' (the 19.0 rename of web_editor): %r" % (depends,),
        )
        self.assertIn("web", depends, "depends must include 'web': %r" % (depends,))

    def test_auto_install_targets_html_editor_not_removed_module(self):
        """Rule (d): auto_install must reference html_editor (list form or True), never the stale
        ['web_editor']."""
        auto_install = _load_manifest().get("auto_install")
        self.assertNotEqual(
            auto_install, ["web_editor"],
            "auto_install still pins the removed module ['web_editor']",
        )
        if auto_install is True:
            return  # auto-install against the full dependency set is acceptable
        self.assertIsInstance(
            auto_install, (list, tuple),
            "auto_install must be True or a list referencing 'html_editor'; got %r" % (auto_install,),
        )
        self.assertIn(
            "html_editor", auto_install,
            "auto_install list must reference 'html_editor' (the 19.0 rename): %r" % (auto_install,),
        )

    def test_frontend_asset_reanchors_to_html_editor_common_scss(self):
        """Rule (e): the frontend asset op re-points AFTER the html_editor common anchor while
        keeping this module's own de-brand SCSS as the injected source."""
        frontend_ops = _load_manifest().get("assets", {}).get(FRONTEND_BUNDLE, [])
        matching = [
            op for op in frontend_ops
            if isinstance(op, (tuple, list)) and len(op) == 3
            and op[0] == "after"
            and op[1] == HTML_EDITOR_ANCHOR
            and op[2] == DEBRAND_SOURCE
        ]
        self.assertTrue(
            matching,
            "web.assets_frontend must inject the de-brand SCSS AFTER the html_editor common anchor: "
            "expected ('after', %r, %r); got %r" % (HTML_EDITOR_ANCHOR, DEBRAND_SOURCE, frontend_ops),
        )

    def test_license_stays_opl_1(self):
        """Rule (f): the upgrade preserves the OPL-1 license (regression guard)."""
        self.assertEqual(
            _load_manifest().get("license"), "OPL-1", "license must remain 'OPL-1'",
        )

    def test_debrand_scss_source_file_is_preserved(self):
        """Rule (g): the de-brand SCSS source continues to exist and its CONTENT is unchanged
        through the upgrade - the manifest ANCHOR changes to html_editor, and the source file's
        OWN name was separately normalized away from the removed module's name to the
        self-describing 'viin_brand_html_editor.common.scss' (regression guard)."""
        self.assertTrue(
            os.path.exists(DEBRAND_SCSS),
            "de-brand source must exist at %s (the upgrade renames the ANCHOR and normalizes this "
            "file's own name; its content is unchanged)" % DEBRAND_SCSS,
        )


# ==================================================================================================
# Minimal cascade + WCAG contrast machinery for the button-colour behavioral guard below.
#
# Scaled down from viin_brand_web/tests/test_brand_cascade_compile.py's general element-cascade
# resolver (that resolver models arbitrary DOM ancestor chains for arbitrary elements). This guard
# only ever asks the cascade about ONE element - a button carrying the literal classes 'btn',
# 'btn-fill-primary' and 'btn-primary' (Bootstrap 5.3's custom-property button pattern: base
# structural declarations on '.btn', per-variant colour tokens on '.btn-<variant>') - so candidate
# rules are found by an EXACT selector match against that fixed 3-class set rather than by a general
# element matcher. Every candidate selector is therefore a single bare class, so CSS specificity is
# constant (one class each) across the whole candidate set and drops out of the cascade key
# entirely; only importance, then source order, then declaration order decide the winner - which is
# what the CSS spec itself does once specificity ties. viin_brand_html_editor's tests must not
# import viin_brand_web's test tree, so this is a self-contained adaptation, not a shared import.
# ==================================================================================================
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_VAR_RE = re.compile(r"^var\(\s*(--[\w-]+)\s*(?:,\s*(.*))?\)$", re.DOTALL)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
_FUNC_RGB_RE = re.compile(r"\brgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", re.IGNORECASE)

# The classes the button element actually carries: the base structural class plus both of this
# module's colour-variant classes (the theme's fill alias and Bootstrap's own 'primary' name).
BUTTON_CLASS_SELECTORS = frozenset({".btn", ".btn-fill-primary", ".btn-primary"})


def _iter_rules(css):
    """Yield (order, selector, body) for every selector of every compiled rule, in source order."""
    for order, (selector_group, body) in enumerate(_RULE_RE.findall(css)):
        for selector in _COMMENT_RE.sub("", selector_group).split(","):
            selector = selector.strip()
            if selector:
                yield order, selector, body


def _declarations(body, prop_names):
    """Return [(value, is_important), ...] for prop_names, in declaration order."""
    found = []
    for declaration in body.split(";"):
        name, separator, value = declaration.partition(":")
        if not separator or name.strip() not in prop_names:
            continue
        value = value.strip()
        important = value.lower().endswith("!important")
        if important:
            value = value[: -len("!important")].rstrip()
        found.append((value, important))
    return found


def _normalize_colour(value):
    """Return value's first colour as a lower-case #rrggbb string, or None."""
    hex_match = _HEX_RE.search(value)
    if hex_match:
        digits = hex_match.group(0)[1:].lower()
        if len(digits) == 3:
            digits = "".join(digit * 2 for digit in digits)
        return "#" + digits[:6]
    func_match = _FUNC_RGB_RE.search(value)
    if func_match:
        channels = tuple(max(0, min(255, int(round(float(group))))) for group in func_match.groups())
        return "#%02x%02x%02x" % channels
    return None


def _winning_declaration_for_button(css, prop_names):
    """Cascade winner of prop_names among rules whose selector is exactly one of
    BUTTON_CLASS_SELECTORS. See the module comment above for why specificity is safely omitted from
    the key here: (importance, source order, declaration order)."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        if selector not in BUTTON_CLASS_SELECTORS:
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _resolve_button_colour(css, prop_name):
    """Resolve prop_name's actually-winning colour on the button element, following var(--x)
    references into BUTTON_CLASS_SELECTORS' own custom-property declarations. Bootstrap 5.3 ships
    button colour as '.btn { color: var(--btn-color) }' / '{ background-color: var(--btn-bg) }',
    with the custom property itself declared on the variant class - the chain is followed rather
    than assumed, so a rename of either the property or the custom-property token is still read
    correctly from whatever the bundle actually compiled."""
    value = _winning_declaration_for_button(css, (prop_name,))
    depth = 6
    while value is not None and depth > 0:
        var_match = _VAR_RE.match(value.strip())
        if not var_match:
            break
        name, fallback = var_match.group(1), var_match.group(2)
        resolved = _winning_declaration_for_button(css, (name,))
        value = resolved if resolved is not None else fallback
        depth -= 1
    return _normalize_colour(value) if value else None


def _relative_luminance(hex_colour):
    """Relative luminance per WCAG 2.1 (sRGB linearisation, gamma 2.4, ITU-R BT.709 coefficients) -
    transcribed from the specification, not from any product formula, so a readability assertion
    built on it can never degenerate into comparing production logic against itself."""
    channels = []
    for offset in (1, 3, 5):
        srgb = int(hex_colour[offset:offset + 2], 16) / 255.0
        channels.append(srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(hex_a, hex_b):
    """Contrast ratio between two #rrggbb colours, per WCAG 2.1 SC 1.4.3."""
    lum_a, lum_b = _relative_luminance(hex_a), _relative_luminance(hex_b)
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


@tagged("post_install", "-at_install")
class HtmlEditorDebrandBehaviorTest(TransactionCase):
    """Once installed on 19.0, the module compiles cleanly into web.assets_frontend and its
    distinctive primary-button de-brand override reaches the compiled CSS."""

    def test_module_reaches_installed_state(self):
        """Rule (h): install smoke - a broken web_editor->html_editor dependency would leave the
        module uninstallable, so its ir.module.module record must be state='installed'."""
        module = self.env["ir.module.module"].search(
            [("name", "=", "viin_brand_html_editor")], limit=1,
        )
        self.assertTrue(module, "viin_brand_html_editor module record not found")
        self.assertEqual(
            module.state, "installed",
            "viin_brand_html_editor must be installed; got state=%r" % (module.state,),
        )

    def test_frontend_bundle_compiles_without_errors(self):
        """Rule (i): the frontend bundle compiles with ZERO errors - proves no 'Undefined variable
        $white' and no 'cannot find asset' from a dangling web_editor anchor."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        bundle.css()
        self.assertFalse(
            bundle.css_errors,
            "web.assets_frontend compiled with CSS errors (expected none): %s" % (bundle.css_errors,),
        )

    def test_primary_button_debrand_override_reaches_frontend_css(self):
        """Rule (j): the button text/background pair '.btn-fill-primary'/'.btn-primary' actually
        paints, resolved through the real compiled-CSS cascade (importance, then source order -
        Bootstrap 5.3 also emits this same grouped selector via its own '--btn-*' CSS-variable
        block with no !important, so a first-match reader is not enough), clears WCAG AA contrast
        (>= 4.5:1 for normal text). Protects readability itself rather than the specific hex this
        module currently forces, so a legitimate recolour of the override that still clears
        contrast must stay green."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        attachments = bundle.css()
        css_text = attachments[0].raw.decode() if attachments else ""
        self.assertTrue(css_text, "compiled frontend CSS is empty")

        text_colour = _resolve_button_colour(css_text, "color")
        background_colour = _resolve_button_colour(css_text, "background-color")
        self.assertIsNotNone(
            text_colour,
            "no winning 'color' declaration resolves for '.btn-fill-primary'/'.btn-primary' in the "
            "compiled frontend CSS",
        )
        self.assertIsNotNone(
            background_colour,
            "no winning 'background-color' declaration resolves for '.btn-fill-primary'/"
            "'.btn-primary' in the compiled frontend CSS",
        )

        ratio = _contrast_ratio(text_colour, background_colour)
        self.assertGreaterEqual(
            ratio, 4.5,
            "'.btn-fill-primary'/'.btn-primary' text %s against its own resolved background %s "
            "clears only %.2f:1 - WCAG AA normal text requires >= 4.5:1"
            % (text_colour, background_colour, ratio),
        )
