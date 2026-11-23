from odoo import api, fields, models

from .res_config_settings import get_settings_app


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    group_ids = fields.Many2many(
        help="If you have groups, the visibility of this menu will be based on these groups. "
             "If this field is empty, Viindoo will compute visibility based on the related object's read access.")

    @api.model
    def _get_hidden_menu_xmlids(self):
        """Return the XML ids of the menus that every user is kept from seeing.

        A listed menu is archived, which takes the menus under it out of the web
        client with it; their actions stay reachable. It is archived whenever the data
        of the module that owns it or of a branding module that lists it is loaded, at
        install and at every update, the way the data of a menu sets it active. An id
        that does not resolve (the module that owns it is not installed) is ignored.
        Branding modules extend the list for the menus of their own app, and give
        their menus back with ``_restore_hidden_menus`` when they are uninstalled.

        :return: a list of fully qualified XML ids
        """
        return []

    def _load_menus_blacklist(self):
        """Leave out the menus that open the settings on an app whose every setting is hidden."""
        blacklist = super()._load_menus_blacklist()
        settings = self.env['res.config.settings']
        if not settings.has_access('read'):
            return blacklist
        # sudo: the menus point at their actions whatever the user may read of them
        actions = self.env['ir.actions.act_window'].sudo().search([('res_model', '=', 'res.config.settings')])
        apps = {action.id: get_settings_app(action.context) for action in actions}
        if not any(apps.values()):
            return blacklist
        unusable = settings._get_unusable_apps()
        dead = ['ir.actions.act_window,%d' % action_id for action_id, app in apps.items() if app in unusable]
        if not dead:
            return blacklist
        # sudo: only the ids of the menus to leave out are read, whatever menus the user may read
        return list(blacklist) + self.sudo().search([('action', 'in', dead)]).ids

    @api.model
    def _get_menus_by_xmlids(self, xmlids):
        menus = self.browse()
        for xmlid in xmlids:
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            if menu and menu._name == self._name:
                menus |= menu
        return menus

    @api.model
    def _archive_hidden_menus(self, xmlids=None):
        """Archive the menus of ``xmlids``.

        :param xmlids: fully qualified XML ids; ``None`` archives every menu of
            ``_get_hidden_menu_xmlids``
        """
        if xmlids is None:
            xmlids = self._get_hidden_menu_xmlids()
        menus = self._get_menus_by_xmlids(xmlids)
        menus.filtered('active').write({'active': False})

    @api.model
    def _restore_hidden_menus(self, xmlids):
        """Make the menus of ``xmlids`` active again."""
        menus = self._get_menus_by_xmlids(xmlids)
        menus.filtered(lambda menu: not menu.active).write({'active': True})

    def _load_records(self, data_list, update=False):
        records = super()._load_records(data_list, update=update)
        # The data of a menu makes it active: a hidden one is archived again on load.
        loaded = {data.get('xml_id') for data in data_list}
        hidden = [xmlid for xmlid in self._get_hidden_menu_xmlids() if xmlid in loaded]
        if hidden:
            self._archive_hidden_menus(hidden)
        return records

    @api.model
    def _update_viin_brand_icons(self):
        from .. import _update_brand_web_icon_data
        _update_brand_web_icon_data(self.env)

    @api.model_create_multi
    def create(self, vals_list):
        from .. import get_viin_brand_module_icon, check_viin_brand_module_icon, _build_viin_web_icon_path_from_image

        for vals in vals_list:
            if 'web_icon' in vals:
                web_icon = vals.get('web_icon')
                paths = web_icon.split(',') if web_icon and isinstance(web_icon, str) else []
                if len(paths) == 2:
                    if check_viin_brand_module_icon(paths[0]):
                        img_path = get_viin_brand_module_icon(paths[0])
                        vals['web_icon'] = _build_viin_web_icon_path_from_image(img_path)
        return super(IrUiMenu, self).create(vals_list)

    def write(self, vals):
        from .. import get_viin_brand_module_icon, check_viin_brand_module_icon, _build_viin_web_icon_path_from_image

        if 'web_icon' in vals:
            web_icon = vals.get('web_icon')
            paths = web_icon.split(',') if web_icon and isinstance(web_icon, str) else []
            if len(paths) == 2:
                if check_viin_brand_module_icon(paths[0]):
                    img_path = get_viin_brand_module_icon(paths[0])
                    vals['web_icon'] = _build_viin_web_icon_path_from_image(img_path)
        return super(IrUiMenu, self).write(vals)
