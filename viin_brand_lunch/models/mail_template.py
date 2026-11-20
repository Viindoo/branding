from odoo import api, models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.model
    def _debrand_lunch_supplier_footer(self):
        """Point the "Powered by" footer of the supplier order mail to Viindoo."""
        template = self.env.ref('lunch.lunch_order_mail_supplier', raise_if_not_found=False)
        if template:
            # plain text: a markup replace would escape the markup of its arguments
            body = str(template.body_html)
            template.body_html = body.replace('https://www.odoo.com', 'https://viindoo.com').replace(
                '>Odoo</a>', '>Viindoo</a>',
            )
