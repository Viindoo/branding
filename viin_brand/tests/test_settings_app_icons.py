from lxml import etree

from odoo.tests.common import TransactionCase, tagged

VIINDOO_APPS_PATH = '/viin_brand/static/img/apps/'


@tagged('post_install', '-at_install')
class TestSettingsAppIcons(TransactionCase):
    """Every app of the Settings side panel shows a Viindoo icon, whatever icon its module ships."""

    def _app_logos(self, view=None):
        arch = self.env['res.config.settings'].get_view(view.id if view else None)['arch']
        return {app.get('name'): app.get('logo') for app in etree.fromstring(arch).xpath('//app[@name]')}

    def test_the_general_settings_app_shows_the_viindoo_settings_icon(self):
        logos = self._app_logos()

        self.assertEqual(logos['general_settings'], VIINDOO_APPS_PATH + 'settings.png')

    def test_an_app_takes_the_viindoo_icon_of_its_module(self):
        view = self.env['ir.ui.view'].create({
            'name': 'viin_brand settings icon test',
            'type': 'form',
            'model': 'res.config.settings',
            'inherit_id': self.env.ref('base.res_config_settings_view_form').id,
            'arch': """
                <xpath expr="//form" position="inside">
                    <app string="CRM" name="crm"><block title="CRM"/></app>
                    <app string="Unknown" name="viin_icon_test_unknown"><block title="Unknown"/></app>
                </xpath>
            """,
        })

        logos = self._app_logos(view)

        self.assertEqual(logos['crm'], VIINDOO_APPS_PATH + 'crm.png')
        # a module without an icon of its own shows the Viindoo base icon, never a missing image
        self.assertEqual(logos['viin_icon_test_unknown'], VIINDOO_APPS_PATH + 'base.png')
