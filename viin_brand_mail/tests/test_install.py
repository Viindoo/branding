# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast
import os

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")


@tagged("post_install", "-at_install")
class TestViinBrandMailInstall(TransactionCase):
    """Smoke: the debranding module installs and depends directly on viin_brand_web.

    Business rule protected: ``viin_brand_mail`` is a debranding overlay on Discuss
    and, once shipped, must be installable and must bring in its declared
    dependencies ``mail`` and ``viin_brand_web`` (the module that now owns every
    SCSS token / Python constant / test helper this module's own tests read).

    Primary RED gate: while the manifest is still ``installable = False`` and the
    stale ``message_seen_indicator.scss`` asset anchor plus undefined SCSS variables
    keep the assets from compiling, ``viin_brand_mail`` cannot be installed - so this
    test is never collected (RED). It turns GREEN only after the module is made
    installable and its assets compile, at which point all three modules report
    ``state == 'installed'``.

    SECONDARY RED gate (the one that actually protects the dependency EDGE, not just
    the resulting registry state): ``state == 'installed'`` alone is satisfiable for
    reasons that have nothing to do with viin_brand_mail's own manifest - another
    module in the same database could pull viin_brand_web in independently, and this
    module's dependency loop would stay green even if viin_brand_mail's own
    ``depends`` list never mentioned viin_brand_web at all. The manifest itself is
    therefore read directly (the same ``ast.literal_eval`` technique this cluster's
    other guards use, e.g. viin_brand_web/tests/test_asset_upgrade.py) and its
    ``depends`` list is asserted to contain ``viin_brand_web`` and to no longer
    contain ``viin_brand_common`` - this is what makes the test capable of failing
    for the RIGHT reason when only the dependency edge regresses.
    """

    def test_debranding_module_and_dependency_chain_are_installed(self):
        module_model = self.env["ir.module.module"]
        for tech_name in ("viin_brand_mail", "mail", "viin_brand_web"):
            module = module_model.search([("name", "=", tech_name)], limit=1)
            self.assertTrue(
                module,
                "Module %r must be present in the module registry" % tech_name,
            )
            self.assertEqual(
                module.state,
                "installed",
                "Module %r must be installed (viin_brand_mail depends on mail + "
                "viin_brand_web)" % tech_name,
            )

    def test_manifest_depends_on_viin_brand_web_not_viin_brand_common(self):
        with open(MANIFEST, encoding="utf-8") as manifest_file:
            manifest = ast.literal_eval(manifest_file.read())
        depends = manifest.get("depends", [])
        self.assertIn(
            "viin_brand_web", depends,
            "viin_brand_mail/__manifest__.py 'depends' must declare viin_brand_web "
            "directly: that module now owns every SCSS token, Python constant, and "
            "test helper this module's own code and tests consume, so the manifest "
            "dependency edge is the business rule under test - not just the "
            "resulting installed state, which other modules can satisfy for "
            "unrelated reasons.",
        )
        self.assertNotIn(
            "viin_brand_common", depends,
            "viin_brand_mail/__manifest__.py 'depends' must no longer declare "
            "viin_brand_common: the tokens/constants/helpers it used to provide "
            "have moved to viin_brand_web, so keeping this edge would depend on a "
            "module that no longer supplies anything this addon reads.",
        )
