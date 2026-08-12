# -*- coding: utf-8 -*-
import ast
import os

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")


@tagged("post_install", "-at_install")
class TestViinBrandOnboardingManifestDepends(TransactionCase):
    """The dependency EDGE from viin_brand_onboarding to the branding base is protected here,
    directly on the manifest text - not on the resulting ``ir.module.module`` install state.

    Business rule (module-boundary refactor, design doc section "viin_brand_onboarding" / the
    `viin_brand_onboarding` row of the 5.3 dependency-rewire table): ``onboarding.scss`` reads
    four brand tokens - ``$o-brand-primary``, ``$o-viin-chrome-base``, ``$o-viin-chrome-deep`` and
    ``$o-brand-secondary`` - that were relocated from ``viin_brand_common`` to ``viin_brand_web``
    in an earlier wave of this same refactor. ``viin_brand_onboarding/__manifest__.py`` must
    therefore declare ``viin_brand_web`` directly in its ``depends`` list and must no longer
    declare ``viin_brand_common``. Getting this wrong is not a silent degradation: Sass aborts
    the WHOLE ``web.assets_backend`` bundle at the first undefined variable
    (``Undefined variable: "$o-viin-chrome-base"``), which serves NO CSS and kills the entire
    backend UI, not just the onboarding panel.

    Reading ``ir.module.module.state`` alone cannot protect this rule: another module in the
    same database can pull ``viin_brand_web`` in independently (it is itself ``auto_install``),
    so the registry could report "installed" for entirely unrelated reasons even if this
    module's own manifest never mentioned ``viin_brand_web`` at all. The manifest file is
    therefore read directly with ``ast.literal_eval`` (the same technique the sibling guards use -
    ``viin_brand_mail/tests/test_install.py::test_manifest_depends_on_viin_brand_web_not_viin_brand_common``,
    ``viin_backend_theme/tests/test_manifest_depends.py``) so the test is capable of failing for
    the RIGHT reason - the dependency edge itself, not a downstream side effect of it.

    Two separate assertIn/assertNotIn calls (not one combined check) so each direction of a
    future regression is independently detectable: dropping ``viin_brand_web`` without re-adding
    ``viin_brand_common`` fails only the first; re-adding ``viin_brand_common`` without dropping
    ``viin_brand_web`` fails only the second.
    """

    def test_manifest_depends_on_viin_brand_web(self):
        with open(MANIFEST, encoding="utf-8") as manifest_file:
            manifest = ast.literal_eval(manifest_file.read())
        depends = manifest.get("depends", [])
        self.assertIn(
            "viin_brand_web", depends,
            "viin_brand_onboarding/__manifest__.py 'depends' must declare viin_brand_web "
            "directly: that module now owns the four SCSS brand tokens "
            "(onboarding.scss reads $o-brand-primary, $o-viin-chrome-base, "
            "$o-viin-chrome-deep, $o-brand-secondary) - the manifest dependency edge is the "
            "business rule under test, not just the resulting installed state, which another "
            "auto_install module in the database can satisfy for unrelated reasons.",
        )

    def test_manifest_does_not_depend_on_viin_brand_common(self):
        with open(MANIFEST, encoding="utf-8") as manifest_file:
            manifest = ast.literal_eval(manifest_file.read())
        depends = manifest.get("depends", [])
        self.assertNotIn(
            "viin_brand_common", depends,
            "viin_brand_onboarding/__manifest__.py 'depends' must no longer declare "
            "viin_brand_common: the SCSS brand tokens it used to contribute to "
            "web._assets_primary_variables have all been relocated to viin_brand_web, so "
            "keeping this edge would depend on a module that no longer supplies anything this "
            "addon's stylesheet reads.",
        )
