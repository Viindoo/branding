import ast
import os
import re

from odoo.tests.common import TransactionCase, tagged

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_BUNDLE = "web.assets_frontend"
REMOVED_MODULE = "web_editor"


def _load_manifest():
    with open(os.path.join(MODULE_DIR, "__manifest__.py"), "r", encoding="utf-8") as manifest_file:
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
    """The manifest depends on html_editor (never on the removed web_editor), is installable,
    keeps its license and injects its own de-brand SCSS after the html_editor common anchor."""

    def test_module_is_installable_001(self):
        """The module is installable."""
        self.assertIs(
            _load_manifest().get("installable"), True,
            "viin_brand_html_editor must be installable=True",
        )

    def test_manifest_has_no_reference_to_removed_web_editor_module(self):
        """No reference to the removed 'web_editor' module appears in depends, in auto_install or
        as a core 'web_editor/static/...' asset anchor; the module's own 'viin_brand_html_editor/...'
        paths do not count."""
        manifest = _load_manifest()

        depends = manifest.get("depends", [])
        self.assertNotIn(
            REMOVED_MODULE, depends,
            "depends lists the removed module 'web_editor': %r" % (depends,),
        )

        auto_install = manifest.get("auto_install")
        if isinstance(auto_install, (list, tuple)):
            self.assertNotIn(
                REMOVED_MODULE, auto_install,
                "auto_install references the removed module 'web_editor': %r" % (auto_install,),
            )

        for token in _iter_asset_tokens(manifest.get("assets", {})):
            self.assertFalse(
                token == REMOVED_MODULE or token.startswith("web_editor/static/"),
                "Asset op anchors the removed 'web_editor/static/...' path: %r" % (token,),
            )

    def test_depends_targets_html_editor_and_web(self):
        """depends lists both html_editor and web."""
        depends = _load_manifest().get("depends", [])
        self.assertIn("html_editor", depends, "depends must include 'html_editor': %r" % (depends,))
        self.assertIn("web", depends, "depends must include 'web': %r" % (depends,))

    def test_auto_install_targets_html_editor_not_removed_module(self):
        """auto_install is True or a list that names html_editor, never ['web_editor']."""
        auto_install = _load_manifest().get("auto_install")
        self.assertNotEqual(
            auto_install, ["web_editor"],
            "auto_install pins the removed module ['web_editor']",
        )
        if auto_install is True:
            return
        self.assertIsInstance(
            auto_install, (list, tuple),
            "auto_install must be True or a list referencing 'html_editor'; got %r" % (auto_install,),
        )
        self.assertIn(
            "html_editor", auto_install,
            "auto_install list must reference 'html_editor': %r" % (auto_install,),
        )

    def test_frontend_asset_anchors_after_html_editor_common_scss_001(self):
        """The frontend bundle injects this module's de-brand SCSS right after the html_editor
        common stylesheet."""
        frontend_ops = _load_manifest().get("assets", {}).get(FRONTEND_BUNDLE, [])
        anchor = "html_editor/static/src/scss/html_editor.common.scss"
        source = "viin_brand_html_editor/static/src/scss/viin_brand_html_editor.common.scss"
        matching = [
            op for op in frontend_ops
            if isinstance(op, (tuple, list)) and tuple(op) == ("after", anchor, source)
        ]
        self.assertTrue(
            matching,
            "web.assets_frontend must inject the de-brand SCSS AFTER the html_editor common anchor: "
            "expected ('after', %r, %r); got %r" % (anchor, source, frontend_ops),
        )

    def test_license_is_opl_1_001(self):
        """The module is licensed OPL-1."""
        self.assertEqual(_load_manifest().get("license"), "OPL-1", "license must be 'OPL-1'")

    def test_debrand_scss_source_file_exists_001(self):
        """The de-brand SCSS source the manifest injects exists on disk."""
        path = os.path.join(MODULE_DIR, "static", "src", "scss", "viin_brand_html_editor.common.scss")
        self.assertTrue(os.path.exists(path), "de-brand source must exist at %s" % path)


# The cascade below resolves one element only - a button carrying the classes 'btn',
# 'btn-fill-primary' and 'btn-primary' - so every candidate selector is a single bare class, specificity
# is constant across the candidates and the winner is decided by importance, then source order,
# then declaration order. The module does not import another module's test tree.
def _iter_rules(css):
    """Yield (order, selector, body) for every selector of every compiled rule, in source order."""
    for order, (selector_group, body) in enumerate(re.findall(r"([^{}]+)\{([^{}]*)\}", css)):
        for selector in re.sub(r"/\*.*?\*/", "", selector_group, flags=re.DOTALL).split(","):
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
    hex_match = re.search(r"#[0-9A-Fa-f]{3,8}\b", value)
    if hex_match:
        digits = hex_match.group(0)[1:].lower()
        if len(digits) == 3:
            digits = "".join(digit * 2 for digit in digits)
        return "#" + digits[:6]
    func_match = re.search(r"\brgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", value, re.IGNORECASE)
    if func_match:
        channels = tuple(max(0, min(255, int(round(float(group))))) for group in func_match.groups())
        return "#%02x%02x%02x" % channels
    return None


def _winning_declaration_for_button(css, prop_names):
    """Cascade winner of prop_names among rules whose selector is exactly '.btn',
    '.btn-fill-primary' or '.btn-primary', ordered by (importance, source order, declaration
    order)."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        if selector not in (".btn", ".btn-fill-primary", ".btn-primary"):
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _resolve_button_colour(css, prop_name):
    """Resolve prop_name's winning colour on the button, following ``var(--x)`` references into the
    button classes' own custom-property declarations."""
    value = _winning_declaration_for_button(css, (prop_name,))
    depth = 6
    while value is not None and depth > 0:
        var_match = re.match(r"^var\(\s*(--[\w-]+)\s*(?:,\s*(.*))?\)$", value.strip(), re.DOTALL)
        if not var_match:
            break
        name, fallback = var_match.group(1), var_match.group(2)
        resolved = _winning_declaration_for_button(css, (name,))
        value = resolved if resolved is not None else fallback
        depth -= 1
    return _normalize_colour(value) if value else None


def _relative_luminance(hex_colour):
    """Relative luminance per WCAG 2.1, transcribed from the specification so that a readability
    assertion built on it never compares production logic against itself."""
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
    """Once installed, the module compiles cleanly into web.assets_frontend and its primary-button
    de-brand override reaches the compiled CSS."""

    def test_module_reaches_installed_state(self):
        """The module installs: its ir.module.module record is in state 'installed'."""
        module = self.env["ir.module.module"].search(
            [("name", "=", "viin_brand_html_editor")], limit=1,
        )
        self.assertTrue(module, "viin_brand_html_editor module record not found")
        self.assertEqual(
            module.state, "installed",
            "viin_brand_html_editor must be installed; got state=%r" % (module.state,),
        )

    def test_frontend_bundle_compiles_without_errors(self):
        """The frontend bundle compiles with no error, so no stylesheet variable is undefined and
        no asset anchor dangles."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        bundle.css()
        self.assertFalse(
            bundle.css_errors,
            "web.assets_frontend compiled with CSS errors (expected none): %s" % (bundle.css_errors,),
        )

    def test_primary_button_text_is_readable_on_its_background_001(self):
        """The primary button's text clears WCAG AA contrast (>= 4.5:1) against its background,
        both resolved through the compiled-CSS cascade."""
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
