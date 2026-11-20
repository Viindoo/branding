from odoo.addons.viin_brand.tests.common import HiddenMenuCase
from odoo.addons.viin_brand_crm import uninstall_hook
from odoo.addons.viin_brand_crm.models.ir_ui_menu import HIDDEN_MENU_XMLIDS
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestPaidLeadServiceMenus(HiddenMenuCase):

    def _load_menu(self, xmlid, values):
        """Load a menu as the data of its module does at the install or update."""
        self.env['ir.ui.menu']._load_records(
            [{'xml_id': xmlid, 'values': dict(values, active=True), 'noupdate': False}],
            update=True,
        )
        return self.env.ref(xmlid)

    def _load_lead_generation_menus(self):
        action = self.env['ir.actions.act_window'].create({
            'name': 'Lead Mining', 'res_model': 'crm.lead',
        })
        generation = self._load_menu('crm_iap_mine.crm_menu_lead_generation', {
            'name': 'Lead Generation',
            'parent_id': self.env.ref('crm.crm_menu_config').id,
        })
        mining = self._load_menu(
            'crm_iap_mine.crm_iap_lead_mining_request_menu_action', {
                'name': 'Lead Mining Requests', 'parent_id': generation.id,
                'action': 'ir.actions.act_window,%d' % action.id,
            },
        )
        return generation, mining

    def test_lead_generation_menus_loaded_after_the_branding_are_archived(self):
        generation, mining = self._load_lead_generation_menus()

        self.assertFalse(generation.active)
        self.assertFalse(mining.active)
        self.assertFalse({generation.id, mining.id} & self.web_client_menu_ids())

    def test_the_lead_generation_menus_come_back_when_the_branding_is_uninstalled(self):
        generation, mining = self._load_lead_generation_menus()

        uninstall_hook(self.env)

        self.assertTrue(generation.active)
        self.assertTrue(mining.active)
        self.assertLessEqual({generation.id, mining.id}, self.web_client_menu_ids())

    def test_the_menus_of_the_installed_paid_lead_services_are_archived(self):
        menus = {
            xmlid: self.env.ref(xmlid, raise_if_not_found=False) for xmlid in HIDDEN_MENU_XMLIDS
        }
        if not any(menus.values()):
            self.skipTest("none of the paid lead services is installed")
        for xmlid, menu in menus.items():
            if menu:
                with self.subTest(menu=xmlid):
                    self.assertFalse(menu.active)
                    self.assertNotIn(menu.id, self.web_client_menu_ids())
