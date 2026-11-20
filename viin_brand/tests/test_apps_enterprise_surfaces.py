from unittest.mock import patch

from odoo.fields import Domain
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged('post_install', '-at_install')
class TestAppsEnterpriseSurfaces(TransactionCase):
    """The Apps lists and their search panel offer nothing that only Enterprise or Odoo can give."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Module = cls.env['ir.module.module']

    def test_every_apps_action_hides_the_enterprise_stubs(self):
        website_apps = self.env.ref('website.action_website_add_features', raise_if_not_found=False)
        if not website_apps:
            website_apps = self.env['ir.actions.act_window'].create({
                'name': 'Website Apps Test', 'res_model': 'ir.module.module',
                'domain': "['!', ('name', '=like', 'theme_%')]",
            })
            self.env['ir.model.data'].create({
                'module': 'website', 'name': 'action_website_add_features', 'model': website_apps._name,
                'res_id': website_apps.id,
            })
        stub = self.Module.create({'name': 'enterprise_stub_apps', 'to_buy': True, 'state': 'uninstallable'})

        for _applied_twice in range(2):
            self.Module._update_domain_for_action()
        found = self.Module.search(Domain(safe_eval(website_apps.domain)) & Domain('id', '=', stub.id))
        domain = website_apps.domain
        self.Module._restore_domain_for_action()

        self.assertFalse(found)
        self.assertEqual(domain.count('to_buy'), 1)
        self.assertNotIn('to_buy', website_apps.domain)
        self.assertIn('theme_', website_apps.domain)

    def test_the_enterprise_flag_is_not_offered_to_filters_and_groupings(self):
        self.assertNotIn('to_buy', self.Module.fields_get())
        self.assertIn('to_buy', self.Module.fields_get(['to_buy']))
        self.assertIn('to_buy', self.Module.fields_get(attributes=['readonly', 'required']))
        for attributes in (['string', 'type'], ['type', 'string', 'required', 'relation', 'exportable']):
            with self.subTest(attributes=attributes):
                self.assertNotIn('to_buy', self.Module.fields_get(attributes=attributes))
        views = self.Module.get_views([(False, 'form')])
        self.assertIn('to_buy', views['models']['ir.module.module']['fields'])

    def test_the_enterprise_flag_is_not_groupable_in_the_fields_the_views_load(self):
        views = self.Module.get_views([(False, 'kanban')])
        fields = views['models']['ir.module.module']['fields']
        self.assertIn('to_buy', fields, 'the kanban card still reads the field')
        self.assertFalse(fields['to_buy']['groupable'])
        self.assertTrue(fields['state']['groupable'])

    def test_categories_with_only_enterprise_modules_leave_the_search_panel(self):
        Category = self.env['ir.module.category']
        enterprise_only = Category.create({'name': 'Enterprise Only Test'})
        community = Category.create({'name': 'Community Test'})
        self.Module.create({
            'name': 'enterprise_only_app', 'to_buy': True, 'application': True, 'state': 'uninstallable',
            'category_id': enterprise_only.id,
        })
        self.Module.create({
            'name': 'community_app', 'application': True, 'state': 'uninstalled', 'category_id': community.id,
        })

        values = self.Module.search_panel_select_range('category_id')['values']

        ids = {value['id'] for value in values}
        self.assertIn(community.id, ids)
        self.assertNotIn(enterprise_only.id, ids)

    def test_the_apps_store_of_odoo_is_never_asked_for_industries(self):
        with patch('requests.post', side_effect=AssertionError('the apps store was asked')):
            self.assertEqual(self.Module._get_industry_categories_from_apps(), [])

    def test_the_module_type_group_leaves_the_search_panel(self):
        arch = (
            '<search><field name="name"/><searchpanel>'
            '<field name="module_type"/><field name="category_id"/></searchpanel></search>'
        )
        with patch('odoo.addons.base.models.ir_ui_view.Base.get_view', return_value={'arch': arch}):
            result = self.Module.get_view(view_type='search')

        self.assertNotIn('module_type', result['arch'])
        self.assertIn('category_id', result['arch'])
