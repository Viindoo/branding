from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # OBS-1 debrand: core `mail.models.res_company` defaults `email_secondary_color`
    # (Settings > General Settings > Email Templates > "Button Color") to '#875A7B' - the
    # legacy Odoo aubergine/purple. Every outgoing notification CTA button
    # (mail/data/mail_templates_email_layouts.xml, the `has_button_access` block) paints its
    # background with `company.email_secondary_color or '#875A7B'`; since this default fills
    # the field at company creation, that fallback literal never actually fires - the stored
    # default IS what renders. Re-key it to Viindoo's brand secondary colour (owner decision
    # D1: '#7f4282', owner-confirmed - the same token viin_brand's apriori.py rewrite already
    # uses for de-branded link colour) rather than a chrome teal: the button text
    # (email_primary_color) stays white, and white-on-#7f4282 is 6.99:1, comfortably clearing
    # WCAG AA normal-text contrast.
    email_secondary_color = fields.Char(default='#7f4282')
