from unittest.mock import patch

from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAppsSearchPanel(TransactionCase):
    """The search panel of the Apps does not group the modules by the apps store of Odoo."""

    def test_the_apps_search_panel_has_no_module_type_field(self):
        arch = self.env['ir.module.module'].get_view(
            self.env.ref('base.view_module_filter').id, 'search',
        )['arch']

        panel = etree.fromstring(arch).xpath('//searchpanel')
        self.assertTrue(panel, 'the Apps search view keeps its search panel')
        self.assertFalse(panel[0].xpath('field[@name="module_type"]'))
        self.assertTrue(panel[0].xpath('field[@name="category_id"]'), 'the categories stay')

    def test_the_module_type_group_leaves_the_search_panel(self):
        arch = (
            '<search><field name="name"/><searchpanel>'
            '<field name="module_type"/><field name="category_id"/></searchpanel></search>'
        )
        with patch('odoo.addons.base.models.ir_ui_view.Base.get_view', return_value={'arch': arch}):
            result = self.env['ir.module.module'].get_view(view_type='search')

        self.assertNotIn('module_type', result['arch'])
        self.assertIn('category_id', result['arch'])
