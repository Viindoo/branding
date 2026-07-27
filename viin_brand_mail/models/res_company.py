from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # OBS-1 debrand: core `mail.models.res_company` defaults `email_secondary_color`
    # (Settings > General Settings > Email Templates > "Button Color") to '#875A7B' - the
    # legacy Odoo aubergine/purple. Every outgoing notification CTA button
    # (mail/data/mail_templates_email_layouts.xml, the `has_button_access` block) paints its
    # background with `company.email_secondary_color or '#875A7B'`; since this default fills
    # the field at company creation, that fallback literal never actually fires - the stored
    # default IS what renders. Re-key it to Viindoo's AA-contrast dark teal
    # ($o-navbar-background / VIINDOO_NAVBAR_BACKGROUND_COLOR, viin_brand_common's
    # brand_variables.scss) rather than the flat brand teal #00BBCE: the button text
    # (email_primary_color) stays white, and white-on-#00BBCE is only 2.33:1 (fails WCAG AA
    # normal-text contrast) while white-on-#007F8E reaches 4.74:1 - the same shade already
    # established for exactly this white-text-on-teal reason, reused here for SSOT rather than
    # inventing a second, nearly-identical dark-teal.
    email_secondary_color = fields.Char(default='#007F8E')
