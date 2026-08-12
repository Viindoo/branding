# Module-boundary relocation guards (ODOO-AI-ETHOS #8: protect the BEHAVIOR/contract the
# content-edit commit must produce, not a snapshot of what exists today).
#
# CONTEXT: commit 1 of this 2-commit refactor did a pure `git mv` of 53 web-layer artefacts from
# viin_brand_common into this module (viin_brand_web), with ZERO content change. The manifest
# merge, the new `data` key, and the `models/` package are still to come in commit 2. These four
# tests specify what commit 2 must produce - see
# designs/viin-brand-common-refactor-2026-08-11.md S:7 "viin_brand_web" table and S:8 hazards 4/5/6/7.
#
# WHAT IS PROTECTED
#  1. The manifest's `assets` dict carries the merged brand-hex SSOT and drops every lingering
#     reference to the retired module name `viin_brand_common` (hazard 6).
#  2. The `static/src/views/widgets/**/*` wildcard glob resolves to a non-empty file set - the one
#     landmine that fails SILENTLY, because Odoo's asset loader only warns on a glob that is NOT
#     itself a wildcard pattern (hazard 4a).
#  3. The 5 moved `data`-loaded templates recombine against their `web.*` parents once the
#     manifest gains a `data` key (hazard 6 / S:5.2).
#  4. `tests/__init__.py` keeps importing the pre-existing `test_about_debrand` module after the
#     coder APPENDS 14 more import lines to it - an overwrite instead of an append would silently
#     de-register that tour test forever (hazard 5b).
import ast
import glob
import os

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MODULE_NAME = os.path.basename(MODULE_DIR)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")
TESTS_INIT = os.path.join(_HERE, "__init__.py")

# The brand-hex SSOT this module's `web._assets_primary_variables` entry must inject once the
# merge lands.
BRAND_VARIABLES_SUFFIX = "viin_brand_web/static/src/scss/brand_variables.scss"

# The 5 moved data-loaded templates and the core `web.*` parent each must recombine against.
MOVED_DATA_TEMPLATES = (
    ("viin_brand_web.brand_promotion_message", "web.brand_promotion_message"),
    ("viin_brand_web.login_layout", "web.login_layout"),
    ("viin_brand_web.webclient_bootstrap", "web.webclient_bootstrap"),
    ("viin_brand_web.report_layout", "web.report_layout"),
    ("viin_brand_web.report_preview_layout", "web.report_preview_layout"),
)


def _load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
        return ast.literal_eval(manifest_file.read())


def _iter_asset_tokens(bundle_ops_by_key):
    """Yield every string token in an ``assets`` mapping, flattening list entries and
    (directive, anchor, source) / (directive, source) tuples."""
    for bundle_ops in bundle_ops_by_key.values():
        for op in bundle_ops:
            if isinstance(op, str):
                yield op
            elif isinstance(op, (tuple, list)):
                for part in op:
                    if isinstance(part, str):
                        yield part


@tagged("post_install", "-at_install")
class RelocationManifestAssetGuardTest(TransactionCase):
    """Hazard 6: the manifest's own asset dict must carry the merged SSOT and no dead token."""

    def test_manifest_declares_merged_web_asset_ssot_and_drops_common_token(self):
        """web._assets_primary_variables injects the brand SSOT; no token names viin_brand_common."""
        manifest = _load_manifest()
        assets = manifest.get("assets", {})

        self.assertIn(
            "web._assets_primary_variables", assets,
            "manifest must declare web._assets_primary_variables once the 53 web-layer assets are "
            "merged in from viin_brand_common - this module's manifest does not carry that bundle "
            "key yet (RED before the content-edit commit).",
        )
        primary_tokens = list(
            _iter_asset_tokens({"web._assets_primary_variables": assets["web._assets_primary_variables"]})
        )
        self.assertTrue(
            any(token.endswith(BRAND_VARIABLES_SUFFIX) for token in primary_tokens),
            "web._assets_primary_variables must inject the brand-hex SSOT %r; got %r"
            % (BRAND_VARIABLES_SUFFIX, primary_tokens),
        )

        common_tokens = [token for token in _iter_asset_tokens(assets) if "viin_brand_common" in token]
        self.assertFalse(
            common_tokens,
            "manifest still ships asset token(s) referencing the retired module name "
            "viin_brand_common: %r. Every asset must point at viin_brand_web after the merge."
            % common_tokens,
        )

    def test_widget_glob_resolves_to_non_empty_file_set(self):
        """The static/src/views/widgets/**/* wildcard glob must match >= 4 files (hazard 4a).

        Odoo's asset loader warns on a non-matching glob ONLY when the pattern is not itself a
        wildcard glob - this pattern IS a wildcard glob, so a zero-file match resolves with NO
        warning at all and the de-brand patches under static/src/views/widgets simply stop being
        loaded. The failure below is split into two distinct assertions so a missing glob TOKEN
        (RED today - the merge has not happened) is never confused with a present-but-empty glob
        MATCH (the silent landmine this guard exists to catch once the merge lands).
        """
        manifest = _load_manifest()
        assets = manifest.get("assets", {})
        widget_glob_tokens = [
            token for token in _iter_asset_tokens(assets)
            if "static/src/views/widgets" in token and "**" in token
        ]
        self.assertTrue(
            widget_glob_tokens,
            "manifest assets dict has no wildcard-glob token under "
            "'static/src/views/widgets/**/*' yet (RED before the content-edit commit merges the "
            "widgets glob in).",
        )

        glob_token = widget_glob_tokens[0]
        # glob_token is ADDONS-relative (e.g. "viin_brand_web/static/src/views/widgets/**/*"), so it
        # already carries this module's own name prefix. MODULE_DIR already ends in that same name,
        # so joining the two directly double-nests the module name; strip the prefix first (same
        # idiom as test_asset_upgrade.py's test_statusbar_step_numbering_is_wired).
        relative_glob = glob_token.split(MODULE_NAME + "/", 1)[1]
        matched_files = [
            path for path in glob.glob(os.path.join(MODULE_DIR, relative_glob), recursive=True)
            if os.path.isfile(path)
        ]
        self.assertGreaterEqual(
            len(matched_files), 4,
            "widget glob %r matched %d file(s) on disk (expected >= 4: documentation_link.js, "
            "documentation_link.xml, viindoo_mapping_url.js, notification_alert.xml under "
            "static/src/views/widgets/). A silent zero-match here is exactly hazard 4a - nothing "
            "else would catch it." % (glob_token, len(matched_files)),
        )


@tagged("post_install", "-at_install")
class RelocationDataTemplateGuardTest(TransactionCase):
    """The 5 moved data templates must recombine against their web.* parents once `data` merges in."""

    def test_moved_data_templates_recombine_against_web_parents(self):
        for xmlid, parent_xmlid in MOVED_DATA_TEMPLATES:
            with self.subTest(xmlid=xmlid):
                view = self.env.ref(xmlid, raise_if_not_found=False)
                self.assertIsNotNone(
                    view,
                    "%s must be a registered data-loaded view once the manifest's `data` key "
                    "merges in views/webclient_template.xml / views/report_templates.xml; not "
                    "found yet (RED before the content-edit commit)." % xmlid,
                )
                self.assertTrue(
                    view.inherit_id,
                    "%s must declare an inherit_id (expected %s)" % (xmlid, parent_xmlid),
                )
                self.assertEqual(
                    view.inherit_id.xml_id, parent_xmlid,
                    "%s.inherit_id must resolve to %s (got %r)"
                    % (xmlid, parent_xmlid, view.inherit_id.xml_id),
                )

    def test_login_layout_recombination_carries_a_debrand_marker(self):
        """At least one recombined arch_db must prove the xpath actually applied a de-brand edit."""
        login_layout = self.env.ref("viin_brand_web.login_layout", raise_if_not_found=False)
        self.assertIsNotNone(
            login_layout,
            "viin_brand_web.login_layout must be registered once the `data` key merges in "
            "views/webclient_template.xml; not found yet (RED before the content-edit commit).",
        )
        self.assertIn(
            "Viindoo", login_layout.arch_db or "",
            "the recombined login_layout arch_db must contain the de-brand marker 'Viindoo', "
            "proving the xpath actually applied.",
        )


class RelocationTestsInitAppendGuardTest(TransactionCase):
    """Hazard 5b: the coder's upcoming append to tests/__init__.py must not become an overwrite."""

    def test_tests_init_still_imports_about_debrand(self):
        """tests/__init__.py must still import test_about_debrand after the 14-line append.

        Currently GREEN: the append has not happened yet, so the original pre-existing line is
        still there untouched. Its protective value is forward-looking - it is what would catch
        the coder silently de-registering the About-block tour test by overwriting this file
        instead of appending to it.
        """
        with open(TESTS_INIT, "r", encoding="utf-8") as init_file:
            source = init_file.read()
        tree = ast.parse(source, filename=TESTS_INIT)
        imported_modules = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertIn(
            "test_about_debrand", imported_modules,
            "tests/__init__.py must still import test_about_debrand (the pre-existing About-block "
            "tour test). An OVERWRITE instead of an APPEND when the coder registers the 14 moved "
            "test modules would silently de-register this tour forever - the tour would simply "
            "stop running, with the suite staying green (hazard 5b).",
        )
