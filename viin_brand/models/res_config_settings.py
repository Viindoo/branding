from lxml import etree

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    favicon = fields.Binary(related='company_id.favicon', readonly=False)

    @api.model
    def get_viin_brand_modules_icon(self, modules):
        # we cannot import outside the class due to the import order in the module's __init__.py
        # i.e. models are imported prior to assigning the `get_viin_brand_module_icon()` to the `get_module_icon()`
        from odoo.modules.module import get_module_icon
        from .. import check_viin_brand_module_icon
        result = []
        if check_viin_brand_module_icon('base'):
            for module in modules:
                result.append(get_module_icon(module))
        return result

    @api.model
    def _get_hidden_setting_xpaths(self):
        """XPaths of the settings every database hides because they only offer Enterprise upsell.

        Branding modules extend the list for the upsell rows of their own app.
        """
        return ['//field[@widget="upgrade_boolean"]/ancestor::setting[1]']

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type != 'form':
            return res
        doc = etree.fromstring(res['arch'])
        self._hide_unusable_settings(doc)
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

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
