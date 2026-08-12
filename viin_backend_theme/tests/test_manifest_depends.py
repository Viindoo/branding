# -*- coding: utf-8 -*-
import ast
import os

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")


@tagged("post_install", "-at_install")
class TestViinBackendThemeManifestDepends(TransactionCase):
    """The dependency EDGE from viin_backend_theme to the branding base is protected here,
    directly on the manifest text - not on the resulting ``ir.module.module`` install state.

    Business rule (module-boundary refactor, design doc section "viin_backend_theme" /
    the `viin_backend_theme` row of the 5.3 dependency-rewire table): every SCSS brand
    token, the ``viin_color_scheme`` preference field + RPC, and the shared brand
    cascade/WCAG test helpers this module's own SCSS and tests read were relocated from
    ``viin_brand_common`` to ``viin_brand_web`` in an earlier wave of this same refactor.
    ``viin_backend_theme/__manifest__.py`` must therefore declare ``viin_brand_web``
    directly in its ``depends`` list and must no longer declare ``viin_brand_common``.

    Reading ``ir.module.module.state`` alone cannot protect this rule: another module in
    the same database can pull ``viin_brand_web`` in independently, so the registry could
    report "installed" for entirely unrelated reasons even if this module's own manifest
    never mentioned ``viin_brand_web`` at all. The manifest file is therefore read
    directly with ``ast.literal_eval`` (the same technique the sibling guard uses -
    ``viin_brand_mail/tests/test_install.py``,
    ``test_manifest_depends_on_viin_brand_web_not_viin_brand_common``) so the test is
    capable of failing for the RIGHT reason - the dependency edge itself, not a
    downstream side effect of it.

    Two separate assertIn/assertNotIn calls (not one combined check) so each direction of
    a future regression is independently detectable: dropping ``viin_brand_web`` without
    re-adding ``viin_brand_common`` fails only the first; re-adding
    ``viin_brand_common`` without dropping ``viin_brand_web`` fails only the second.
    """

    def test_manifest_depends_on_viin_brand_web(self):
        with open(MANIFEST, encoding="utf-8") as manifest_file:
            manifest = ast.literal_eval(manifest_file.read())
        depends = manifest.get("depends", [])
        self.assertIn(
            "viin_brand_web", depends,
            "viin_backend_theme/__manifest__.py 'depends' must declare viin_brand_web "
            "directly: that module now owns the SCSS brand tokens this theme's own "
            "stylesheets read (9+ files), the viin_color_scheme preference field + RPC "
            "the appearance systray calls, and the shared brand cascade/WCAG test "
            "helpers this module's own test suite imports - the manifest dependency "
            "edge is the business rule under test, not just the resulting installed "
            "state, which another module in the database can satisfy for unrelated "
            "reasons.",
        )

    def test_manifest_does_not_depend_on_viin_brand_common(self):
        with open(MANIFEST, encoding="utf-8") as manifest_file:
            manifest = ast.literal_eval(manifest_file.read())
        depends = manifest.get("depends", [])
        self.assertNotIn(
            "viin_brand_common", depends,
            "viin_backend_theme/__manifest__.py 'depends' must no longer declare "
            "viin_brand_common: the SCSS tokens, the viin_color_scheme field/RPC, and "
            "the test helpers it used to provide have all been relocated to "
            "viin_brand_web, so keeping this edge would depend on a module that no "
            "longer supplies anything this addon reads.",
        )
