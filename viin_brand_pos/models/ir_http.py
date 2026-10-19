from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        # The customer display is a public page: it only receives the web translations of the
        # modules listed here, so without this one this module's terms stay untranslated there.
        mods = super()._get_translation_frontend_modules_name()
        return mods + ['viin_brand_pos']
