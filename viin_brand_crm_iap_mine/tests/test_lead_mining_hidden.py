from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import HiddenMenuCase
from odoo.addons.viin_brand_crm_iap_mine import uninstall_hook

LEAD_MINING_MENUS = (
    'crm_iap_mine.crm_menu_lead_generation',
    'crm_iap_mine.crm_iap_lead_mining_request_menu_action',
)


@tagged('post_install', '-at_install')
class TestLeadMiningHidden(HiddenMenuCase):

    def _load_menu(self, xmlid, values):
        """Load a menu as the data of its module does at the install or update."""
        self.env['ir.ui.menu']._load_records(
            [{'xml_id': xmlid, 'values': dict(values, active=True), 'noupdate': False}],
            update=True,
        )
        return self.env.ref(xmlid)

    def test_the_lead_mining_menus_are_archived_until_the_uninstall(self):
        menus = [self.env.ref(xmlid) for xmlid in LEAD_MINING_MENUS]
        for menu in menus:
            self.assertFalse(menu.active, menu.complete_name)
            self.assertNotIn(menu.id, self.web_client_menu_ids())

        uninstall_hook(self.env)

        for menu in menus:
            self.assertTrue(menu.active, menu.complete_name)
        self.assertLessEqual({menu.id for menu in menus}, self.web_client_menu_ids())

    def test_the_lead_mining_menus_loaded_again_are_archived(self):
        menu = self.env.ref('crm_iap_mine.crm_menu_lead_generation')
        menu = self._load_menu('crm_iap_mine.crm_menu_lead_generation', {
            'name': menu.name, 'parent_id': menu.parent_id.id,
        })
        self.assertFalse(menu.active)
        self.assertNotIn(menu.id, self.web_client_menu_ids())
