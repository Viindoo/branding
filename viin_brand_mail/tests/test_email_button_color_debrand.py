# Part of Odoo. See LICENSE file for full copyright and licensing details.
from types import SimpleNamespace

from lxml import html

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
            company.email_secondary_color, '#7F4282',
            "New company's email button color must default to Viindoo's brand secondary colour",
        )

    def test_existing_company_still_on_odoo_purple_is_normalized_by_post_init_hook(self):
        from .. import post_init_hook

        company = self.env['res.company'].create({'name': 'Legacy Purple Co'})
        company.write({'email_secondary_color': '#875A7B'})  # simulate a pre-upgrade record
        post_init_hook(self.env)
        self.assertEqual(
            company.email_secondary_color, '#7F4282',
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


@tagged("post_install", "-at_install")
class TestNotificationEmailTakesTheCompanyColour(TransactionCase):
    """The button and the footer link of the notification layouts take the colour of the company.

    The layouts are views, so the colour does not depend on the language the email is rendered in,
    including one activated after the module was installed.
    """

    LANGUAGES = ("en_US", "vi_VN", "fr_FR")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for lang in cls.LANGUAGES[1:]:
            cls.env["res.lang"]._activate_lang(lang)

    def _render(self, layout_xmlid, company, lang):
        rendered = self.env["mail.render.mixin"].with_context(lang=lang)._render_encapsulate(
            layout_xmlid,
            "<p>Body</p>",
            add_context={
                "company": company,
                "has_button_access": True,
                "button_access": {"url": "https://example.com/open", "title": "Open"},
                "email_notification_force_footer": True,
            },
        )
        return html.fromstring(str(rendered))

    def test_the_button_and_the_footer_link_take_the_company_colour_in_every_language(self):
        company = self.env["res.company"].create({"name": "Colour Co", "email_secondary_color": "#123456"})
        for layout_xmlid in ("mail.mail_notification_layout", "mail.mail_notification_light"):
            for lang in self.LANGUAGES:
                with self.subTest(layout=layout_xmlid, lang=lang):
                    tree = self._render(layout_xmlid, company, lang)
                    link = tree.xpath("//a[contains(@href, 'viindoo.com')]")[0]
                    self.assertIn("#123456", link.get("style"))
                    if layout_xmlid == "mail.mail_notification_layout":
                        button_cell = tree.xpath("//a[@href='https://example.com/open']/..")[0]
                        self.assertIn("#123456", button_cell.get("style"))

    def test_a_company_without_a_colour_falls_back_to_the_brand_colour(self):
        company = self.env["res.company"].create({"name": "No Colour Co"})
        company.email_secondary_color = False
        tree = self._render("mail.mail_notification_layout", company, "en_US")
        button_cell = tree.xpath("//a[@href='https://example.com/open']/..")[0]
        link = tree.xpath("//a[contains(@href, 'viindoo.com')]")[0]
        for element in (button_cell, link):
            self.assertIn("#7F4282", element.get("style"))
            self.assertNotIn("#875A7B", element.get("style").upper())

    def _render_invitation(self, company):
        user = SimpleNamespace(company_id=company)
        rendered = self.env["ir.qweb"]._render(
            "mail.discuss_channel_invitation_template",
            {
                "base_url": "https://example.com",
                "channel": self.env["discuss.channel"],
                "invitation_url": "/chat/1",
                "mail_body": "<p>Hello</p>",
                "user": user,
            },
            minimal_qcontext=True,
        )
        return html.fromstring(str(rendered)).xpath("//a[@href='https://example.com/chat/1']")[0]

    def test_the_channel_invitation_button_takes_the_company_colour(self):
        company = self.env["res.company"].create({"name": "Invite Co", "email_secondary_color": "#123456"})
        self.assertIn("#123456", self._render_invitation(company).get("style"))

    def test_the_channel_invitation_button_of_a_company_without_a_colour_is_the_brand_colour(self):
        company = self.env["res.company"].create({"name": "Invite No Colour Co"})
        company.email_secondary_color = False
        style = self._render_invitation(company).get("style")
        self.assertIn("#7F4282", style)
        self.assertNotIn("#875A7B", style.upper())
