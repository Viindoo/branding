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
        """Rule (j): the module's distinctive grouped override '.btn-fill-primary, .btn-primary'
        forcing white text with !important survives into the compiled frontend CSS. Bootstrap 5.3
        ALSO emits this same grouped selector via its own '--btn-*' CSS-variable block (with NO
        !important), so the test iterates every occurrence of the grouping to locate THIS module's
        own override block - identified by a white color (#fff/#ffffff) AND !important together in
        the SAME declaration block - rather than assuming the grouping itself is unique."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        attachments = bundle.css()
        css_text = attachments[0].raw.decode() if attachments else ""
        self.assertTrue(css_text, "compiled frontend CSS is empty")

        # Minification-robust: strip ALL whitespace + lowercase, then locate the grouped selector.
        compact = re.sub(r"\s+", "", css_text).lower()
        grouped_selector = ".btn-fill-primary,.btn-primary"
        self.assertIn(
            grouped_selector, compact,
            "the module's distinctive grouped selector '.btn-fill-primary, .btn-primary' is absent "
            "from the compiled frontend CSS - the de-brand override did not reach web.assets_frontend",
        )

        # Locate THIS module's override block among ALL grouped-selector occurrences.
        # Bootstrap 5.3 emits the SAME '.btn-fill-primary,.btn-primary' grouping as a '--btn-*'
        # CSS-variable block with NO '!important', so a first-hit str.find() locator lands on the
        # WRONG block; iterate ALL occurrences to find THIS module's own override block, then assert
        # at least one carries BOTH a white color and !important in the same declaration block.
        override_found = False
        for match in re.finditer(re.escape(grouped_selector), compact):
            pos = match.start()
            brace = compact.find("}", pos)
            block = compact[pos: brace + 1] if brace != -1 else compact[pos:]
            if ("#fff" in block or "#ffffff" in block) and "!important" in block:
                override_found = True
                break
        self.assertTrue(
            override_found,
            "no compiled '.btn-fill-primary,.btn-primary' declaration block forces a WHITE color "
            "(#fff/#ffffff) with !important - this module's own de-brand override "
            "'.btn-fill-primary,.btn-primary{color:#fff!important}' did not reach web.assets_frontend. "
            "Bootstrap 5.3 also groups '.btn-fill-primary,.btn-primary' as a '--btn-*' CSS-variable "
            "block with no !important, so its mere presence does NOT satisfy this rule.",
        )
