from lxml import etree

from odoo.fields import Domain
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import convert_file
from odoo.tools.safe_eval import safe_eval

ARCH = """
<form>
    <app name="kept">
        <block title="Kept">
            <setting id="plain"><field name="company_id"/></setting>
            <setting id="installable"><field name="module_base_import"/></setting>
        </block>
        <block title="Emptied">
            <setting id="upsell"><field name="module_enterprise_only" widget="upgrade_boolean"/></setting>
            <setting id="no_module"><field name="module_ghost"/></setting>
        </block>
    </app>
    <app name="emptied">
        <block title="Emptied too">
            <setting id="upsell_too"><field name="module_other_enterprise" widget="upgrade_boolean"/></setting>
        </block>
    </app>
</form>
"""


@tagged('post_install', '-at_install')
class TestHideEnterpriseUpsell(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env['res.config.settings']
        cls.env['ir.module.module'].create({'name': 'ghost', 'state': 'uninstallable'})

    def test_hides_upsell_settings_and_the_containers_they_empty(self):
        doc = etree.fromstring(ARCH)

        self.settings._hide_unusable_settings(doc)

        hidden = {
            node.get('id') or node.get('title') or node.get('name')
            for node in doc.xpath('//*[@invisible="1"]')
        }
        self.assertEqual(
            hidden,
            {'upsell', 'no_module', 'upsell_too', 'Emptied', 'Emptied too', 'emptied'},
        )

    def test_real_settings_view_hides_the_upsell_setting_and_its_app(self):
        view = self.env['ir.ui.view'].create({
            'name': 'viin_brand upsell test',
            'type': 'form',
            'model': 'res.config.settings',
            'inherit_id': self.env.ref('base.res_config_settings_view_form').id,
            'arch': """
                <xpath expr="//form" position="inside">
                    <app string="Upsell" name="viin_upsell_test">
                        <block title="Upsell">
                            <setting id="viin_upsell_test">
                                <field name="module_base_import" widget="upgrade_boolean"/>
                            </setting>
                        </block>
                    </app>
                </xpath>
            """,
        })

        doc = etree.fromstring(self.settings.get_view(view.id)['arch'])

        self.assertEqual(doc.xpath('//setting[@id="viin_upsell_test"]')[0].get('invisible'), '1')
        self.assertEqual(doc.xpath('//app[@name="viin_upsell_test"]')[0].get('invisible'), '1')

    def test_apps_action_hides_to_buy_modules_and_keeps_other_domains(self):
        Module = self.env['ir.module.module']
        stub = Module.create({'name': 'enterprise_stub', 'to_buy': True, 'state': 'uninstallable'})
        theme = Module.create({'name': 'theme_stub', 'state': 'uninstalled'})
        action = self.env.ref('base.open_module_tree')
        action.domain = "['!', ('name', '=like', 'theme_%')]"

        for _loaded_twice in range(2):
            convert_file(self.env, 'viin_brand', 'data/viin_brand_data.xml', None)

        candidates = stub | theme | Module.search([('name', '=', 'base')])
        found = Module.search(Domain(safe_eval(action.domain)) & Domain('id', 'in', candidates.ids))
        self.assertEqual(found.mapped('name'), ['base'])
        self.assertEqual(action.domain.count('to_buy'), 1)

    def test_restoring_the_apps_action_drops_only_the_to_buy_condition(self):
        Module = self.env['ir.module.module']
        action = self.env.ref('base.open_module_tree')
        action.domain = "['!', ('name', '=like', 'theme_%')]"
        convert_file(self.env, 'viin_brand', 'data/viin_brand_data.xml', None)

        Module._restore_domain_for_action()

        self.assertNotIn('to_buy', action.domain)
        theme = Module.create({'name': 'theme_stub', 'state': 'uninstalled'})
        self.assertFalse(Module.search(Domain(safe_eval(action.domain)) & Domain('id', '=', theme.id)))

        action.domain = "[('to_buy', '=', False)]"
        Module._restore_domain_for_action()
        self.assertFalse(action.domain)
