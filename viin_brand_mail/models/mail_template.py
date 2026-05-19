from odoo import fields, models

try:
    from odoo.addons.viin_brand.apriori import mail_template_terms
except ImportError:
    mail_template_terms = []


class MailTemplate(models.Model):
    _inherit = "mail.template"

    auto_delete = fields.Boolean(help="This option permanently removes any track of email after it's been sent, "
        "including from the Technical menu in the Settings, in order to preserve storage space of your Viindoo database.")

    def _render_field(self, field, res_ids, *args, **kwargs):
        """Replace Odoo branding with Viindoo branding in rendered email fields."""
        results = super()._render_field(field, res_ids, *args, **kwargs)
        if mail_template_terms and field in ('body_html', 'subject'):
            for res_id, value in results.items():
                if value and 'Odoo' in str(value):
                    for old, new in mail_template_terms:
                        value = value.replace(old, new)
                    results[res_id] = value
        return results
