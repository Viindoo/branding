from odoo import models


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    def _run_action_sms_multi(self, eval_context=None):
        # An automation runs unattended: its SMS fail with the not-configured sentence instead of
        # interrupting the record change that triggered it.
        return super(IrActionsServer, self.with_context(viin_brand_sms_automated=True))._run_action_sms_multi(
            eval_context=eval_context,
        )
