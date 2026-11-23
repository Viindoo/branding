from lxml import etree

from odoo.tests.common import TransactionCase, tagged

from ..models.res_config_settings import get_settings_app

UPSELL_APP = 'viin_brand_upsell_only'


@tagged('post_install', '-at_install')
class TestSettingsEntryPoints(TransactionCase):
    """Every settings action and menu opens on an app the settings page shows."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # An app whose only setting sells an Enterprise module, the way core's Maintenance app is.
        cls.env['ir.ui.view'].create({
            'name': 'viin_brand upsell only app',
            'type': 'form',
            'model': 'res.config.settings',
            'inherit_id': cls.env.ref('base.res_config_settings_view_form').id,
            'arch': """
                <xpath expr="//form" position="inside">
                    <app string="Upsell Only" name="%s">
                        <block title="Upsell">
                            <setting id="viin_brand_upsell_only_setting">
                                <field name="module_voip" widget="upgrade_boolean"/>
                            </setting>
                        </block>
                    </app>
                </xpath>
            """ % UPSELL_APP,
        })
        cls.action = cls.env['ir.actions.act_window'].create({
            'name': 'Upsell Only Settings',
            'res_model': 'res.config.settings',
            'view_mode': 'form',
            'context': "{'module': '%s', 'bin_size': False}" % UPSELL_APP,
        })
        cls.env['ir.ui.menu'].create({
            'name': 'Upsell Only Settings',
            'parent_id': cls.env.ref('base.menu_administration').id,
            'action': 'ir.actions.act_window,%d' % cls.action.id,
        })
        cls.admin = cls.env.ref('base.user_admin')

    def _hidden_apps(self):
        """Return the apps the settings page the administrator loads has no tab for."""
        views = self.env['res.config.settings'].with_user(self.admin).get_views([(False, 'form')])
        doc = etree.fromstring(views['views']['form']['arch'])
        return {app.get('name') for app in doc.xpath('//app[@invisible="1"]')}

    def _settings_actions(self):
        return self.env['ir.actions.act_window'].search([('res_model', '=', 'res.config.settings')])

    def test_every_settings_action_opens_on_an_app_the_page_shows(self):
        hidden = self._hidden_apps()
        self.assertIn(UPSELL_APP, hidden, 'an app holding only an upsell has no tab')
        for action in self._settings_actions():
            # what the web client receives when it opens the action
            # sudo: reads the whole action; core filters it with `sudo(False)`.
            context = action.with_user(self.admin).sudo()._get_action_dict()['context']
            with self.subTest(action=action.name):
                self.assertNotIn(get_settings_app(context), hidden)

    def test_upsell_only_action_still_opens_the_settings(self):
        # sudo: reads the whole action; core filters it with `sudo(False)`.
        result = self.action.with_user(self.admin).sudo()._get_action_dict()
        self.assertEqual(result['res_model'], 'res.config.settings')
        self.assertIsNone(get_settings_app(result['context']), 'the page opens on its first app')
        self.assertIn("'bin_size': False", result['context'], 'the rest of the context is kept')

    def test_no_menu_opens_the_settings_on_an_app_the_page_hides(self):
        hidden = self._hidden_apps()
        menus = self.env['ir.ui.menu'].with_user(self.admin).load_menus(debug=False)
        loaded_actions = {
            menu['action_id'] for menu in menus.values() if menu.get('action_model') == 'ir.actions.act_window'
        }
        for action in self._settings_actions().filtered(lambda action: action.id in loaded_actions):
            with self.subTest(action=action.name):
                self.assertNotIn(get_settings_app(action.context), hidden)

    def test_menu_of_an_app_the_page_shows_stays(self):
        menus = self.env['ir.ui.menu'].with_user(self.admin).load_menus(debug=False)
        general = self.env.ref('base_setup.menu_config')
        self.assertIn(general.id, menus, 'the General Settings menu is still loaded')
