from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import LazyTranslate

_lt_core = LazyTranslate('base_import_module')

# Plain lookup keys: the sentences core raises, translated through the catalog of the module that
# owns them.
CORE_STUDIO_CUSTOMIZATIONS_ERROR = _lt_core('Studio customizations require the Odoo Studio app.')
CORE_MISSING_DEPENDENCIES_INTRO = _lt_core(
    "The installation of the data module would fail as the following dependencies can't"
    " be found in the addons-path:\n"
)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    total_lines_of_code = fields.Integer(help="Number of lines of code of the module.")

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """Drop the module-type group of the search panel, which lists the apps store of Odoo."""
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == 'search':
            doc = etree.fromstring(result['arch'])
            panel_fields = doc.xpath('//searchpanel/field[@name="module_type"]')
            if panel_fields:
                for node in panel_fields:
                    node.getparent().remove(node)
                result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    @api.model
    def _get_missing_dependencies(self, zip_data):
        """Describe the missing dependencies without the offer of an edition or a download."""
        description, unavailable_modules = super()._get_missing_dependencies(zip_data)
        if unavailable_modules:
            description = CORE_MISSING_DEPENDENCIES_INTRO._translate(self.env.lang or 'en_US')
            description += ''.join('- %s\n' % module for module in unavailable_modules)
        return description, unavailable_modules

    def _import_module(self, module, path, force=False, with_demo=False):
        try:
            return super()._import_module(module, path, force=force, with_demo=with_demo)
        except UserError as error:
            core_message = CORE_STUDIO_CUSTOMIZATIONS_ERROR._translate(self.env.lang or 'en_US')
            if error.args and error.args[0] == core_message:
                raise UserError(_(
                    "These customizations cannot be imported: "
                    "the tool they were made with is not available in Viindoo."
                )) from error
            raise
