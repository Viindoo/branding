# Deterministic upgrade guards (DESIGN 2.1 / 2.2 / 4b-J2 / 4d / 5, ODOO-AI-ETHOS #8):
#   * the manifest ships no retired de-brand/theme source and keeps only the brand-var SSOT;
#   * the DocumentationLink URL map is re-keyed to odoo 19.0 so it matches core's computed URLs;
#   * the retired visual SCSS is gone and brand_variables.scss is a clean var-only file, while
#     the graph-palette core/colors/colors.js is intentionally PRESENT again as a v19 3-arg brand
#     override (teal-first getColor/getColors), wired eagerly into web.assets_backend.
# These protect the "no dangling asset / no competing token layer / map matches core / brand graph
# palette wired" business rules by reading the module's own source - no live instance needed.
import ast
import os
import re

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")
DOC_MAP_JS = os.path.join(
    MODULE_DIR, "static", "src", "views", "widgets", "documentation_link", "viindoo_mapping_url.js"
)
BRAND_VARIABLES_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "brand_variables.scss")

# viin_brand_web-OWNED source paths that the visual-theme retirement removes. Only tokens that
# reference this module are checked - a surviving CORE insertion anchor such as
# 'web/static/src/scss/primary_variables.scss' (the anchor brand_variables.scss is injected before)
# is NOT owned by this module and must not trip the guard.
# NOTE: "core/colors/colors.js" is deliberately NOT listed here - it was retired in the initial v19
# upgrade but re-added as the intentional v19 3-arg brand graph-palette override; its presence and
# wiring are asserted positively by test_graph_palette_override_is_wired below.
RETIRED_ASSET_FRAGMENTS = (
    "scss/primary_variables.scss",
    "scss/bootstrap_overridden.scss",
    "scss/bootstrap_review_frontend.scss",
    "scss/helpers_backport.scss",
    "legacy/scss/",
    "search/",
    "views/fields/",
    "views/form/button_box/",
    "webclient/navbar/",
    "webclient/settings_form_view/",
    "webclient/webclient.scss",
)

# Asset-bundle keys whose whole op is removed with the SCSS retirement (DESIGN 5 slim manifest).
RETIRED_BUNDLE_KEYS = (
    "web._assets_core",
    "web._assets_bootstrap_frontend",
    "web._assets_secondary_variables",
    "web._assets_backend_helpers",
    "web._assets_helpers",
)

# Files that must be deleted from disk with the retirement (DESIGN 2.2 / 4d).
# core/colors/colors.js is NOT listed: it is intentionally present again (brand graph palette) -
# see test_graph_palette_override_is_wired.
RETIRED_ON_DISK = (
    os.path.join(MODULE_DIR, "static", "src", "scss", "bootstrap_overridden.scss"),
    os.path.join(MODULE_DIR, "static", "src", "scss", "primary_variables.scss"),
)

# The intentional v19 graph-palette override (re-added after the initial retirement dropped it).
COLORS_JS = os.path.join(MODULE_DIR, "static", "src", "core", "colors", "colors.js")

# Deliberate v19 RE-OCCUPANTS of a retired path, named one by one.
#
# Same contract as core/colors/colors.js above, and for the same reason: the fragment list stays
# BROAD so nothing else can creep back under `views/fields/`, and anything that legitimately lives
# there again is enumerated here AND asserted positively by its own test - never by loosening the
# fragment. A retirement guard that gets narrowed every time someone needs the path back stops
# guarding anything.
#
# The statusbar STEP-NUMBER unit (owner request 2026-08-03). What `views/fields/` retired was the
# 18.0 visual SCSS theme layer - whole-widget restyles. This is the opposite shape: an ordinal on
# core's own arrow steps, added as a class + a data attribute + one `::after`, with core's chevron
# geometry, click handling and DOM text all untouched (guarded by
# tests/test_brand_cascade_compile.py::
# test_the_statusbar_numbering_layer_declares_no_step_or_container_geometry). It sits on core's own
# path because that is where a reader looks for it.
#
# res_config_edition.xml - a PRE-EXISTING viin_brand_web asset (present in this module before the
# viin_brand_common relocation; DESIGN_DOC viin-brand-common-refactor-2026-08-11.md S:5.2 marks it
# "PRE-EXISTING, keep"). It has nothing to do with the 18.0 visual-theme retirement this guard
# otherwise protects; it merely happens to sit under the historically-retired
# `webclient/settings_form_view/` fragment. This guard could never see it before the relocation - it
# only ever filtered tokens carrying the `viin_brand_common/` prefix, and this token was never in
# that module's manifest. Now that the guard scans this module's OWN full manifest, the collision is
# real but harmless: allow-listed here rather than by loosening RETIRED_ASSET_FRAGMENTS.
INTENTIONAL_ASSETS_UNDER_RETIRED_PATHS = frozenset({
    "viin_brand_web/static/src/views/fields/statusbar/statusbar_steps.js",
    "viin_brand_web/static/src/views/fields/statusbar/statusbar_steps.xml",
    "viin_brand_web/static/src/views/fields/statusbar/statusbar_steps.scss",
    "viin_brand_web/static/src/core/webclient/settings_form_view/widgets/res_config_edition.xml",
})


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
class AssetUpgradeGuardTest(TransactionCase):

    def test_manifest_has_no_dangling_retired_asset(self):
        """Manifest ships NO retired theme/de-brand source and wires the brand-var SSOT only."""
        manifest = _load_manifest()
        assets = manifest.get("assets", {})
        self.assertTrue(assets, "manifest must still declare an 'assets' block")

        viin_tokens = [t for t in _iter_asset_tokens(assets) if "viin_brand_web/" in t]
        for token in viin_tokens:
            if token in INTENTIONAL_ASSETS_UNDER_RETIRED_PATHS:
                continue
            for fragment in RETIRED_ASSET_FRAGMENTS:
                self.assertNotIn(
                    fragment, token,
                    "Retired asset still shipped by the manifest: %r (matches %r). The visual SCSS "
                    "theme layer is retired (DESIGN 2.2/4d)." % (token, fragment),
                )

        for key in RETIRED_BUNDLE_KEYS:
            self.assertNotIn(
                key, assets,
                "Retired asset-bundle key still present in manifest: %r (its whole op is removed "
                "with the SCSS retirement)." % key,
            )

        # The one brand-var SSOT must be injected into the surviving primary-variables bundle.
        self.assertIn(
            "web._assets_primary_variables", assets,
            "manifest must keep web._assets_primary_variables to inject the brand-var SSOT",
        )
        primary_tokens = list(
            _iter_asset_tokens({"web._assets_primary_variables": assets["web._assets_primary_variables"]})
        )
        self.assertTrue(
            any(
                t.endswith("viin_brand_web/static/src/scss/brand_variables.scss")
                for t in primary_tokens
            ),
            "web._assets_primary_variables must reference "
            "viin_brand_web/static/src/scss/brand_variables.scss (the brand-hex SSOT); got %r"
            % primary_tokens,
        )

    def test_doc_link_map_is_rekeyed_to_19(self):
        """DocumentationLink map KEYS are re-keyed to odoo 19.0 (else they never match core's URLs)."""
        self.assertTrue(os.path.exists(DOC_MAP_JS), "viindoo_mapping_url.js must exist at %s" % DOC_MAP_JS)
        with open(DOC_MAP_JS, "r", encoding="utf-8") as js_file:
            js = js_file.read()
        # Map KEYS are the www.odoo.com documentation URLs; the values point at viindoo.com and are
        # intentionally excluded by scoping the version match to the odoo.com key namespace.
        key_versions = set(re.findall(r"www\.odoo\.com/documentation/(\d+\.\d+)", js))
        self.assertTrue(key_versions, "no www.odoo.com documentation KEYS found in the map")
        self.assertNotIn(
            "18.0", key_versions, "map still has stale 18.0 documentation KEYS - must re-key to 19.0"
        )
        self.assertNotIn(
            "17.0", key_versions, "map still has stale 17.0 documentation KEYS - must re-key to 19.0"
        )
        self.assertIn(
            "19.0", key_versions,
            "map has no 19.0 documentation KEYS - core 19.0 builds .../documentation/19.0/... URLs",
        )
        self.assertEqual(
            key_versions, {"19.0"},
            "every www.odoo.com documentation KEY must be 19.0 (else it can never match core's "
            "computed URL); found %r" % sorted(key_versions),
        )

    def test_graph_palette_override_is_wired(self):
        """The brand graph-palette colors.js is present on disk and wired eagerly into the backend.

        Re-adding it after the initial v19 retirement is intentional: core exposes chart series
        colours only through the getColor/getColors exports of core/colors/colors.js, and the only
        supported seam to retint them is an eager export reassignment (there is no registry /
        CSS-var / arch hook). This guard replaces the retirement assertion that previously covered
        the same file, so the two cannot silently disagree.
        """
        self.assertTrue(
            os.path.exists(COLORS_JS),
            "brand graph-palette override must exist at %s" % COLORS_JS,
        )
        with open(COLORS_JS, "r", encoding="utf-8") as colors_file:
            colors_src = colors_file.read()
        # It must retint via the writable exports and lead with the brand teal (teal-first).
        self.assertIn(
            "colors.getColor =", colors_src,
            "colors.js must reassign the getColor export (the seam core chart renderers read)",
        )
        self.assertIn(
            "#00BBCE", colors_src,
            "colors.js must ship the Viindoo brand teal as the leading series colour",
        )
        # It must be wired EAGERLY (a bare string entry) into web.assets_backend, else the lazy
        # graph/pivot/dashboard consumers snapshot core's palette before the override runs.
        manifest = _load_manifest()
        backend_ops = manifest.get("assets", {}).get("web.assets_backend", [])
        self.assertIn(
            "viin_brand_web/static/src/core/colors/colors.js", backend_ops,
            "colors.js must be an eager (bare-string) entry in web.assets_backend; got %r"
            % backend_ops,
        )

    def test_statusbar_step_numbering_is_wired(self):
        """The statusbar step-number unit exists on disk and all three files are in the backend.

        The positive half of INTENTIONAL_ASSETS_UNDER_RETIRED_PATHS - the same two-sided contract
        test_graph_palette_override_is_wired uses. The retirement guard skips these three tokens, so
        without this test that skip would be a hole: a stale entry could name a deleted file, or the
        unit could be half-wired (JS present, template missing), and nothing would notice. Each file
        is therefore asserted BOTH to exist and to be an eager bare-string entry in
        web.assets_backend - eager because a template extension and a prototype patch must be live
        before the first form view renders, and web.assets_backend because the marker is painted in
        `currentColor` and so needs no separate dark-bundle arm.
        """
        manifest = _load_manifest()
        backend_ops = manifest.get("assets", {}).get("web.assets_backend", [])
        for token in sorted(INTENTIONAL_ASSETS_UNDER_RETIRED_PATHS):
            path = os.path.join(MODULE_DIR, token.split("viin_brand_web/", 1)[1])
            self.assertTrue(
                os.path.exists(path),
                "%r is allow-listed past the `views/fields/` retirement guard but does not exist. "
                "Either restore the file or drop it from INTENTIONAL_ASSETS_UNDER_RETIRED_PATHS - a "
                "stale entry silently widens that guard." % token,
            )
            self.assertIn(
                token, backend_ops,
                "%r must be an eager (bare-string) entry in web.assets_backend: the statusbar "
                "numbering is a template extension plus a prototype patch, so it has to be loaded "
                "before the first form view renders. Got %r." % (token, backend_ops),
            )

    def test_visual_scss_theme_layer_is_retired(self):
        """Retired visual SCSS is gone; brand_variables.scss is a clean var-only SSOT."""
        for path in RETIRED_ON_DISK:
            self.assertFalse(
                os.path.exists(path), "Retired file must be deleted (DESIGN 2.2/4d): %s" % path
            )
        self.assertTrue(
            os.path.exists(BRAND_VARIABLES_SCSS),
            "brand_variables.scss (slim brand-hex SSOT) must exist at %s" % BRAND_VARIABLES_SCSS,
        )
        with open(BRAND_VARIABLES_SCSS, "r", encoding="utf-8") as scss_file:
            scss = scss_file.read()
        self.assertNotIn(
            "!important", scss, "brand_variables.scss must carry NO !important (no competing token layer)"
        )
        self.assertNotIn(
            ":root", scss, "brand_variables.scss must carry NO :root rule (variables only, no runtime CSS)"
        )
        self.assertNotIn(
            "darken(", scss, "brand_variables.scss must not use deprecated Dart-Sass darken()"
        )
        self.assertNotIn(
            "lighten(", scss, "brand_variables.scss must not use deprecated Dart-Sass lighten()"
        )
