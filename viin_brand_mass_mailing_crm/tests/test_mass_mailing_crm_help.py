# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from unittest.mock import patch

from odoo.tests.common import TransactionCase, new_test_user, tagged

from odoo.addons.mass_mailing_crm.models.mailing_mailing import MailingMailing as CoreMailing


@tagged("post_install", "-at_install")
class TestMassMailingCrmHelp(TransactionCase):

    def test_leads_helper_names_viindoo_not_odoo(self):
        mailing = self.env["mailing.mailing"].create({"subject": "Newsletter"})

        action = mailing.action_redirect_to_leads_and_opportunities()

        self.assertIn("Viindoo", action["help"])
        self.assertNotIn("Odoo", action["help"])

    def test_statistics_email_tip_without_lead_has_no_link_to_odoo(self):
        user = new_test_user(
            self.env, login="mailing_owner_stats", groups="base.group_user,sales_team.group_sale_salesman",
        )
        mailing = self.env["mailing.mailing"].create({"subject": "Newsletter", "user_id": user.id})
        self.assertFalse(mailing.crm_lead_count)

        values = mailing.with_user(user)._prepare_statistics_email_values()

        # Another module (Mass Mailing Sales) may rename the block of the leads: it is the tip that is looked for.
        tips = [str(kpi["kpi_tip"]) for kpi in values["kpi_data"] if kpi.get("kpi_tip")]
        self.assertTrue(tips, "a mailing without a lead tells its owner how to get some")
        for tip in tips:
            self.assertNotIn("odoo.com", tip)
            self.assertNotIn("<a ", tip)
            self.assertTrue(tip.strip())

    def test_statistics_email_tip_loses_its_link_when_another_module_renames_the_lead_block(self):
        """Another module may rename the block of the leads and a module of its own may add a tip."""
        user = new_test_user(
            self.env, login="mailing_owner_renamed", groups="base.group_user,sales_team.group_sale_salesman",
        )
        mailing = self.env["mailing.mailing"].create({"subject": "Newsletter", "user_id": user.id})
        core_values = CoreMailing._prepare_statistics_email_values

        def values_of_another_module(record):
            values = core_values(record)
            values["kpi_data"][1]["kpi_name"] = "renamed"
            values["kpi_data"][0]["kpi_tip"] = "A tip of another module"
            return values

        with patch.object(CoreMailing, "_prepare_statistics_email_values", values_of_another_module):
            values = mailing.with_user(user)._prepare_statistics_email_values()

        lead_block, other_block = values["kpi_data"][1], values["kpi_data"][0]
        self.assertNotIn("odoo.com", str(lead_block["kpi_tip"]))
        self.assertNotIn("<a ", str(lead_block["kpi_tip"]))
        self.assertTrue(str(lead_block["kpi_tip"]).strip())
        self.assertEqual(other_block["kpi_tip"], "A tip of another module")
