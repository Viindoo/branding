import re

from odoo import api, models

DEMO_TEMPLATE_XMLID = 'crm.mail_template_demo_crm_lead'
# The footer anchor of the demo template: any link to the site of Odoo whose text is the product name.
POWERED_BY_LINK = re.compile(r'(<a [^>]*?)href="https://www\.odoo\.com[^"]*"([^>]*>)Odoo</a>')


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.model
    def _debrand_crm_demo_template(self):
        """Take the product name out of the welcome mail of the demo leads, which exists in a demo database only."""
        template = self.env.ref(DEMO_TEMPLATE_XMLID, raise_if_not_found=False)
        if template:
            # plain text: a markup replace would escape the quotes of the anchor
            current = str(template.body_html or '')
            body = current.replace('get the most out of Odoo', 'get the most out of our solutions')
            body = POWERED_BY_LINK.sub(r'\1href="https://viindoo.com"\2Viindoo</a>', body)
            if body != current:
                template.body_html = body
