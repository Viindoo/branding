from unittest.mock import patch

from odoo.addons.base.wizard.base_module_update import BaseModuleUpdate
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

    def test_the_apps_list_hides_the_enterprise_stubs(self):
        apps = self.env.ref('base.open_module_tree')
        stub = self.Module.create({'name': 'enterprise_stub_apps', 'to_buy': True, 'state': 'uninstallable'})
        # A module installed beside this one (Website) may keep a condition of its own on the list,
        # which hides the themes: restoring the list leaves that condition as it was.
        theme = self.Module.create({'name': 'theme_stub_apps', 'state': 'uninstalled'})

        def listed(modules):
            domain = Domain(safe_eval(apps.domain)) if apps.domain else Domain.TRUE
            return self.Module.search(domain & Domain('id', 'in', modules.ids))

        theme_listed_before = theme in listed(theme)

        for _applied_twice in range(2):
            self.Module._update_domain_for_action()
        found = listed(stub)
        domain = apps.domain
        self.Module._restore_domain_for_action()

        self.assertFalse(found)
        self.assertEqual(domain.count('to_buy'), 1)
        self.assertNotIn('to_buy', apps.domain or '')
        self.assertIn(stub, listed(stub))
        self.assertEqual(theme in listed(theme), theme_listed_before)

    def test_an_apps_list_added_by_another_module_keeps_its_own_domain(self):
        """A module that extends ``_get_apps_actions`` gets the same treatment on top of its domain."""
        other_apps = self.env['ir.actions.act_window'].create({
            'name': 'Other Apps Test', 'res_model': 'ir.module.module',
            'domain': "['!', ('name', '=like', 'theme_%')]",
        })
        stub = self.Module.create({'name': 'enterprise_stub_apps', 'to_buy': True, 'state': 'uninstallable'})

        with patch.object(type(self.Module), '_get_apps_actions', return_value=other_apps):
            for _applied_twice in range(2):
                self.Module._update_domain_for_action()
            found = self.Module.search(Domain(safe_eval(other_apps.domain)) & Domain('id', '=', stub.id))
            domain = other_apps.domain
            self.Module._restore_domain_for_action()

        self.assertFalse(found)
        self.assertEqual(domain.count('to_buy'), 1)
        self.assertIn('theme_', domain)
        self.assertNotIn('to_buy', other_apps.domain)
        self.assertIn('theme_', other_apps.domain)

    def test_the_apps_opened_after_updating_the_list_hide_the_enterprise_stubs(self):
        """"Open Apps" of the update wizard lists every module but the Enterprise stubs, nothing else changes."""
        stub = self.Module.create({'name': 'enterprise_stub_apps', 'to_buy': True, 'state': 'uninstallable'})
        community = self.Module.create({'name': 'community_stub_apps', 'state': 'uninstalled'})
        wizard = self.env['base.module.update'].create({})

        action = wizard.action_module_open()

        listed = self.Module.search(Domain(safe_eval(action['domain'])))
        self.assertIn(community, listed)
        self.assertNotIn(stub, listed)
        self.assertEqual(listed, self.Module.search([('to_buy', '=', False)]))
        core_action = BaseModuleUpdate.action_module_open(wizard)
        self.assertEqual(
            {key: value for key, value in action.items() if key != 'domain'},
            {key: value for key, value in core_action.items() if key != 'domain'},
        )

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
