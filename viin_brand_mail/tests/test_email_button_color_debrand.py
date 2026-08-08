# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEmailButtonColorDebrand(TransactionCase):
    """The outgoing-notification CTA button must never default to Odoo's legacy aubergine.

    core ``mail.models.res_company`` defaults ``email_secondary_color`` to ``#875A7B``. That
    field paints the background of the ``has_button_access`` CTA button rendered by
    ``mail/data/mail_templates_email_layouts.xml`` (``company.email_secondary_color or
    '#875A7B'``) and is pre-filled as the "Button Color" swatch on
    Settings > General Settings > Email Templates. Because the field is populated at company
    creation, the template's ``... or '#875A7B'`` fallback never actually fires - the stored
    default is what paints the button - so the field default itself must be de-branded
    (viin_brand_mail/models/res_company.py), and any company already on the untouched core
    default must be normalized on install (viin_brand_mail's post_init_hook).
    """

    def test_new_company_button_color_defaults_to_viindoo_not_odoo_purple(self):
        company = self.env['res.company'].create({'name': 'Acceptance Debrand Co'})
        self.assertNotEqual(
            company.email_secondary_color, '#875A7B',
            "New company must not default to Odoo's legacy aubergine/purple button color",
        )
        self.assertEqual(
            company.email_secondary_color, '#7f4282',
            "New company's email button color must default to Viindoo's brand secondary colour",
        )

    def test_existing_company_still_on_odoo_purple_is_normalized_by_post_init_hook(self):
        from .. import post_init_hook

        company = self.env['res.company'].create({'name': 'Legacy Purple Co'})
        company.write({'email_secondary_color': '#875A7B'})  # simulate a pre-upgrade record
        post_init_hook(self.env)
        self.assertEqual(
            company.email_secondary_color, '#7f4282',
            "post_init_hook must normalize a company still on Odoo's legacy purple to "
            "Viindoo's brand secondary colour",
        )

    def test_existing_company_with_explicit_custom_color_is_left_untouched(self):
        from .. import post_init_hook

        company = self.env['res.company'].create({'name': 'Custom Color Co'})
        company.write({'email_secondary_color': '#123456'})
        post_init_hook(self.env)
        self.assertEqual(
            company.email_secondary_color, '#123456',
            "post_init_hook must not overwrite a company's explicitly chosen button color",
        )
