# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestViinBrandMailInstall(TransactionCase):
    """Smoke: the debranding module installs and pulls its full dependency chain.

    Business rule protected: ``viin_brand_mail`` is a debranding overlay on Discuss
    and, once shipped, must be installable and must bring in its declared
    dependencies ``mail`` and ``viin_brand_common``.

    Primary RED gate: while the manifest is still ``installable = False`` and the
    stale ``message_seen_indicator.scss`` asset anchor plus undefined SCSS variables
    keep the assets from compiling, ``viin_brand_mail`` cannot be installed - so this
    test is never collected (RED). It turns GREEN only after the module is made
    installable and its assets compile, at which point all three modules report
    ``state == 'installed'``.
    """

    def test_debranding_module_and_dependency_chain_are_installed(self):
        module_model = self.env["ir.module.module"]
        for tech_name in ("viin_brand_mail", "mail", "viin_brand_common"):
            module = module_model.search([("name", "=", tech_name)], limit=1)
            self.assertTrue(
                module,
                "Module %r must be present in the module registry" % tech_name,
            )
            self.assertEqual(
                module.state,
                "installed",
                "Module %r must be installed (viin_brand_mail depends on mail + "
                "viin_brand_common)" % tech_name,
            )
