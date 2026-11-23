import ast

from lxml import etree

from odoo import api, fields, models


def get_settings_context(context):
    """Return the context of a settings action as a dict, ``None`` when it is not a literal dict."""
    try:
        values = ast.literal_eval(context or '{}')
    except (ValueError, SyntaxError):
        return None
    return values if isinstance(values, dict) else None


def get_settings_app(context):
    """Return the settings app the context of an action opens on, ``None`` when it names none."""
    return (get_settings_context(context) or {}).get('module')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    favicon = fields.Binary(related='company_id.favicon', readonly=False)

    @api.model
    def _get_hidden_setting_xpaths(self):
        """XPaths of the settings every database hides.

        The list holds the settings that only offer Enterprise upsell and the one that sells a paid
        service of Odoo (company suggestions). Branding modules extend the list for the rows of their
        own app.
        """
        return [
            '//field[@widget="upgrade_boolean"]/ancestor::setting[1]',
            '//setting[@id="partner_autocomplete"]',
        ]

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type != 'form':
            return res
        doc = etree.fromstring(res['arch'])
        self._hide_unusable_settings(doc)
        self._brand_app_logos(doc)
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.model
    def _get_unusable_apps(self):
        """Return the names of the settings apps whose every setting is hidden.

        Such an app has no tab on the settings page, so an action or a menu that opens the page on it
        has nothing to show.
        """
        doc = etree.fromstring(self.get_view(view_type='form')['arch'])
        return {app.get('name') for app in doc.xpath('//app[@invisible="1"]')}

    @api.model
    def _brand_app_logos(self, doc):
        """Give every app of the settings side panel its Viindoo icon.

        The settings compiler builds the icon of an app from its ``logo`` attribute.
        """
        # imported here: the models load before `get_module_icon` is replaced by the Viindoo resolver
        from odoo.modules.module import get_module_icon
        for app in doc.xpath('//app[@name]'):
            logo = get_module_icon(app.get('name'))
            if logo:
                app.set('logo', logo)

    @api.model
    def _hide_unusable_settings(self, doc):
        """Hide the settings a user can neither use nor ask for, then the blocks and apps they empty."""
        # reading the module state is not sensitive, and a settings user may lack access to ir.module.module
        unavailable = {
            module.name for module in self.env['ir.module.module'].sudo().search([('state', '=', 'uninstallable')])
        }
        hidden = [
            field.getparent() for field in doc.xpath('//field[starts-with(@name, "module_")]')
            if field.get('name')[len('module_'):] in unavailable
        ]
        for xpath in self._get_hidden_setting_xpaths():
            hidden += doc.xpath(xpath)
        for node in hidden:
            node.set('invisible', '1')

        for container_tag, child_tag in (('block', 'setting'), ('app', 'block')):
            for container in doc.xpath('//%s' % container_tag):
                if all(child.tag == child_tag and child.get('invisible') == '1' for child in container):
                    container.set('invisible', '1')
