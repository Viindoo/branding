# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Manifest guards for the viin_brand_common -> viin_brand_web POS rewire.

Business rules protected (see
designs/viin-brand-common-refactor-2026-08-11.md S:5.3 the viin_brand_pos
row, S:8 hazard 4c, S:9 the viin_brand_pos acceptance block):

1. viin_brand_pos/__manifest__.py's ``depends`` list must name the module
   that owns the brand-token SSOT (``viin_brand_web``), never the retired
   name (``viin_brand_common``) it used to name.
2. Every asset ANCHOR PATH this manifest declares inside the POS bundle must
   resolve to a file that actually exists, resolved through Odoo's OWN
   module-path lookup - the same addons path the live registry loaded from -
   never a bare filesystem join against this module's own directory. Two of
   the three anchors point at files owned by ANOTHER module (point_of_sale);
   the third is about to move to a third module (viin_brand_web). An
   anchor that cannot be resolved raises a LOUD ``ValueError`` at the first
   SCSS bundle build (``AssetPaths._raise_not_found`` in
   odoo/addons/base/models/ir_asset.py:432 - "File(s) %s not found in bundle
   %s"), not at plain module install: ``viin_brand_common`` still exists as
   an installable module even though its ``static/src/scss/`` subtree is
   gone, so a plain ``-i viin_brand_pos`` succeeds on a broken manifest and
   this guard is the only thing that catches the defect before a bundle
   build ever runs.
"""
import ast
import os

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")


def _load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
        return ast.literal_eval(manifest_file.read())


def _iter_anchor_tuples(assets):
    """Yield ``(bundle_key, directive, anchor_token, source_token)`` for
    every 3-element ``(directive, anchor, source)`` asset op across all
    bundles in an ``assets`` mapping.

    A 2-element op like ``('prepend', 'path/to/file.scss')`` or a bare
    string carries no anchor - only a 3-element ``('after'/'before', anchor,
    source)`` tuple pins a file relative to another file already present in
    the bundle, so only those carry a resolvable anchor path.
    """
    for bundle_key, bundle_ops in assets.items():
        for op in bundle_ops:
            if isinstance(op, (tuple, list)) and len(op) == 3:
                directive, anchor, source = op
                yield bundle_key, directive, anchor, source


def _resolve_via_module_path(token):
    """Resolve an addons-relative asset token (``<module>/<rest...>``) to an
    absolute filesystem path via Odoo's own module resolution.

    This walks the SAME addons path the live registry actually loaded from -
    never a bare ``os.path.join(MODULE_DIR, token)`` against this module's
    own directory, which would be wrong for any anchor owned by another
    module (as two of the three anchors here are) and would also risk a
    false GREEN from a stale file that happens to exist elsewhere on disk
    under a different addons-path ordering. Returns ``None`` when the token
    has no ``module/relative_path`` shape, or when the named module itself
    cannot be found on the addons path at all.
    """
    module_name, separator, relative_path = token.partition("/")
    if not separator:
        return None
    module_path = get_module_path(module_name, display_warning=False)
    if not module_path:
        return None
    return os.path.join(module_path, relative_path)


@tagged("post_install", "-at_install")
class TestViinBrandPosManifestDependsGuard(TransactionCase):
    """The manifest's ``depends`` edge must name the brand-token SSOT owner.

    RED today: ``viin_brand_pos/__manifest__.py`` still declares
    ``viin_brand_common`` and does not declare ``viin_brand_web`` (the
    module that owns the brand-token SSOT once the refactor lands).
    Asserting on the manifest's own ``depends`` list - not on installed
    registry state - is what makes this test capable of failing for the
    dependency EDGE itself: another module in the same database pulling
    ``viin_brand_web`` in independently would leave a registry-state check
    green even if this module's own manifest never named it (the same
    ``ast.literal_eval`` idiom used by
    ``viin_brand_mail/tests/test_install.py``).
    """

    def test_manifest_depends_on_viin_brand_web_not_viin_brand_common(self):
        manifest = _load_manifest()
        depends = manifest.get("depends", [])
        self.assertIn(
            "viin_brand_web", depends,
            "viin_brand_pos/__manifest__.py 'depends' must declare "
            "viin_brand_web directly: that module owns the brand-token "
            "SSOT (brand_variables.scss) this module's POS bundle anchors "
            "against, so the dependency edge is the business rule under "
            "test - not just resulting installed state, which another "
            "module can satisfy for unrelated reasons.",
        )
        self.assertNotIn(
            "viin_brand_common", depends,
            "viin_brand_pos/__manifest__.py 'depends' must no longer "
            "declare viin_brand_common: its static/src/scss tree has moved "
            "away in full, so keeping this edge would depend on a module "
            "that no longer supplies the SCSS this addon's bundle anchors "
            "against.",
        )


@tagged("post_install", "-at_install")
class TestViinBrandPosAssetAnchorResolutionGuard(TransactionCase):
    """Every asset anchor in this manifest must resolve to a real file.

    RED today on the brand-token anchor specifically: the manifest's
    ``point_of_sale._assets_pos`` bundle anchors
    ``viin_brand_pos/static/src/scss/pos_variables.scss`` ``'after'``
    ``viin_brand_common/static/src/scss/brand_variables.scss`` - but
    ``viin_brand_common``'s entire ``static/src/scss/`` tree has been
    relocated away in this worktree (confirmed: no ``static/`` directory
    exists under ``viin_brand_common`` at all any more), so that anchor
    target does not exist anywhere on the live addons path. Odoo's asset
    resolver (``AssetPaths.index`` / ``_raise_not_found`` in
    odoo/addons/base/models/ir_asset.py:432) raises a LOUD ``ValueError``
    the first time this bundle is actually built - not at plain module
    install, which can succeed on a broken manifest because
    ``viin_brand_common`` still exists as an installable module. This guard
    exists to catch that class of defect before a bundle build ever runs.

    The other two anchors in the same bundle - into ``point_of_sale``'s
    ``pos.scss`` and ``error_handlers.js`` - are unaffected by this
    refactor and are asserted here too, as control/regression coverage: a
    resolution check that only ever exercised the one broken anchor would
    not prove the resolution MECHANISM itself is correct for anchors owned
    by modules other than this one.
    """

    def test_every_manifest_asset_anchor_resolves_to_an_existing_file(self):
        manifest = _load_manifest()
        assets = manifest.get("assets", {})
        anchor_tuples = list(_iter_anchor_tuples(assets))
        self.assertGreater(
            len(anchor_tuples), 0,
            "sanity: viin_brand_pos/__manifest__.py must declare at least "
            "one anchor ('after'/'before') asset tuple to protect - none "
            "found, so this guard would otherwise vacuously pass.",
        )
        for bundle_key, directive, anchor, source in anchor_tuples:
            with self.subTest(bundle=bundle_key, directive=directive, anchor=anchor):
                resolved = _resolve_via_module_path(anchor)
                self.assertIsNotNone(
                    resolved,
                    "asset anchor %r in bundle %r (source %r) names a "
                    "module that cannot be found on the addons path at "
                    "all - resolved via Odoo's own module-path lookup, "
                    "never a bare filesystem join." % (anchor, bundle_key, source),
                )
                self.assertTrue(
                    os.path.isfile(resolved),
                    "asset anchor %r in bundle %r (source %r) does not "
                    "resolve to an existing file (resolved to %r) via "
                    "Odoo's own module-path lookup - the same addons path "
                    "the live registry loads from. A directive anchored "
                    "'after'/'before' a target that does not exist raises "
                    "a LOUD ValueError at the first SCSS bundle build "
                    "(ir_asset.py's AssetPaths._raise_not_found)."
                    % (anchor, bundle_key, source, resolved),
                )
