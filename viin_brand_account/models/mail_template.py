from odoo import api, models

# The logo of the e-invoice notification mails, as core writes it and as it is replaced.
CORE_LOGO = 'alt="Odoo" src="/web/static/img/logo_inverse_white_206px.png"'
BRAND_LOGO = 'alt="Viindoo" src="/viin_brand/static/img/Viindoo-logo-inverted.svg"'
EINVOICE_TEMPLATE_XMLIDS = [
    'account.mail_template_einvoice_notification',
    'account.mail_template_invoice_subscriber',
]


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.model
    def _debrand_account_einvoice_templates(self):
        """Replace the product logo in the header of the e-invoice notification mails."""
        for xmlid in EINVOICE_TEMPLATE_XMLIDS:
            template = self.env.ref(xmlid, raise_if_not_found=False)
            if not template:
                continue
            # plain text: a markup replace would escape the quotes of the logo tag
            body = str(template.body_html or '')
            if CORE_LOGO in body:
                template.body_html = body.replace(CORE_LOGO, BRAND_LOGO)
