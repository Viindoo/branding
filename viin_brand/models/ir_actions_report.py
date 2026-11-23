from odoo import api, models
from odoo.exceptions import RedirectWarning, UserError

from ..tools import brand_pdf, debrand_exception


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _handle_merge_pdfs_error(self, error=None, error_stream=None):
        try:
            return super()._handle_merge_pdfs_error(error=error, error_stream=error_stream)
        except UserError as user_error:
            raise debrand_exception(user_error)

    @api.model
    def _merge_pdfs(self, streams, handle_error=None):
        try:
            return super()._merge_pdfs(streams, handle_error=handle_error)
        except UserError as user_error:
            raise debrand_exception(user_error)

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        try:
            content, report_type = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        except RedirectWarning as warning:
            raise debrand_exception(warning)
        if report_type == 'pdf' and isinstance(content, bytes):
            content = brand_pdf(content)
        return content, report_type
