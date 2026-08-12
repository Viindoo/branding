# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Manifest guard for the viin_brand_common -> viin_brand_base_setup rename (ODOO-AI-ETHOS #8).

Business rule (module-boundary refactor - see DESIGN_DOC
viin-brand-common-refactor-2026-08-11.md S:5.1/6/9): wave 1 already relocated this module's
entire core-`web` half into `viin_brand_web` and rewired all 7 inbound dependency edges, so this
wave's rename is purely module-local. The residual module keeps its git identity (`git mv`) and
becomes an honestly-named, dependency-free auto-install leaf:
  * it carries `old_technical_name: 'viin_brand_common'` (D1) - a truthful marker plus the
    `to_base` lint-whitelist entry (`to_base/__init__.py:235`), NOT an install-state migration -
    core Odoo reads this key nowhere;
  * it drops the direct `web` edge (D2 - `web` stays reachable transitively through
    `base_setup`/`viin_brand`, so nothing crashes; the value of dropping it is that the manifest
    becomes a truthful statement of what the module may touch);
  * `auto_install` flips `['web'] -> True` ATOMICALLY with dropping `web` from `depends` - leaving
    `auto_install: ['web']` after removing `web` from `depends` is an `AssertionError` at manifest
    parse time (`odoo/modules/module.py:450-456`, the `set(auto_install).difference(depends)`
    check);
  * `price` follows the content: `9.9 -> 0.0` (D9 - the paid 53-file web half moved to
    `viin_brand_web` in wave 1, which now carries the price instead).

This guard reads the module's OWN `__manifest__.py` directly via `ast.literal_eval` (never through
`ir.module.module` - a database read cannot distinguish "this module declares the right depends"
from "some OTHER module in the same database pulled the same dependency in", so it is incapable of
failing for the right reason) resolved RELATIVE TO THIS FILE, so the test keeps working whether it
runs from `viin_brand_common/tests/` (pre-rename, RED) or `viin_brand_base_setup/tests/`
(post-rename, GREEN) without any path hardcoded to either module name.
"""
import ast
import os

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")

OLD_NAME = "viin_brand_common"
NEW_NAME = "viin_brand_base_setup"


def _load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
        return ast.literal_eval(manifest_file.read())


def _iter_string_values(value):
    """Recursively yield every string literal anywhere inside a manifest value
    (dict / list / tuple / set / str)."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for sub in value.values():
            yield from _iter_string_values(sub)
    elif isinstance(value, (list, tuple, set)):
        for sub in value:
            yield from _iter_string_values(sub)


@tagged("post_install", "-at_install")
class RenameManifestGuardTest(TransactionCase):
    """The rename lands with the exact manifest shape D1/D2/D9 require - nothing more, nothing
    less. Every assertion here is RED before the rename and GREEN once it lands."""

    def test_old_technical_name_marks_the_rename(self):
        """Rule (a) - D1: the module truthfully declares the name it was renamed from."""
        manifest = _load_manifest()
        self.assertEqual(
            manifest.get("old_technical_name"), OLD_NAME,
            "manifest must declare old_technical_name='viin_brand_common' (D1) - the rename "
            "marker and to_base lint-whitelist entry, got %r" % (manifest.get("old_technical_name"),),
        )

    def test_depends_drops_the_direct_web_edge(self):
        """Rule (b) - D2: the direct `web` edge is dropped (web stays reachable transitively via
        base_setup/viin_brand, so this is a truthfulness improvement, not a functional one)."""
        depends = _load_manifest().get("depends", [])
        self.assertNotIn("web", depends, "depends must not declare 'web' directly (D2): %r" % (depends,))

    def test_auto_install_is_true_not_the_stale_web_list(self):
        """Rule (c): auto_install must be True, atomically with dropping 'web' from depends -
        leaving ['web'] here after that drop is an AssertionError at manifest parse time."""
        self.assertIs(
            _load_manifest().get("auto_install"), True,
            "auto_install must be True (normalises to set(depends)), not the stale ['web'] list",
        )

    def test_price_follows_the_content_to_zero(self):
        """Rule (d) - D9: the price follows the content; the paid web half moved to
        viin_brand_web in wave 1, so this residual module is free."""
        self.assertEqual(
            _load_manifest().get("price"), 0.0,
            "price must be 0.0 (D9) - the paid content moved to viin_brand_web in wave 1",
        )

    def test_manifest_carries_no_other_reference_to_the_old_name(self):
        """Rule (e) - acceptance clause 3: the ONLY manifest value anywhere allowed to reference
        'viin_brand_common' is the old_technical_name value itself; a third survivor is a defect.
        Also confirms the assets key was removed entirely (design S:5.1 - zero SCSS/JS remains
        after the wave-1 split moved every asset into viin_brand_web)."""
        manifest = _load_manifest()
        self.assertFalse(
            manifest.get("assets"),
            "manifest must carry no 'assets' key (or an empty one) - this module ships zero "
            "SCSS/JS after the wave-1 split: %r" % (manifest.get("assets"),),
        )
        offenders = []
        for key, value in manifest.items():
            if key == "old_technical_name":
                continue
            for token in _iter_string_values(value):
                if OLD_NAME in token:
                    offenders.append("%s: %r" % (key, token))
        self.assertFalse(
            offenders,
            "manifest carries a reference to '%s' outside old_technical_name: %s" % (OLD_NAME, offenders),
        )


@tagged("post_install", "-at_install")
class RenameInstallSmokeTest(TransactionCase):
    """Once the rename lands, the module must actually reach state='installed' under its NEW
    technical name - a broken depends/auto_install edit would leave it uninstallable."""

    def test_module_reaches_installed_state_under_new_name(self):
        module = self.env["ir.module.module"].search([("name", "=", NEW_NAME)], limit=1)
        self.assertTrue(module, "%s module record not found" % (NEW_NAME,))
        self.assertEqual(
            module.state, "installed",
            "%s must be installed; got state=%r" % (NEW_NAME, module.state),
        )
