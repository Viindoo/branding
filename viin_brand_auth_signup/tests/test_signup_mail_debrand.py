# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from unittest.mock import patch
from urllib.parse import urlsplit

from lxml import html

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.translate import LazyTranslate

from odoo.addons.base.models.ir_qweb import IrQweb

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)
LAYOUT = "mail.mail_notification_layout"


@tagged("post_install", "-at_install")
class TestSignupMailDebrand(TransactionCase):

    def test_signup_mail_templates_name_no_odoo_and_link_no_odoo_page(self):
        for xmlid in (
            "auth_signup.set_password_email",
            "auth_signup.mail_template_user_signup_account_created",
            "auth_signup.mail_template_data_unregistered_users",
            "auth_signup.portal_set_password_email",
        ):
            template = self.env.ref(xmlid).with_context(lang="en_US")
            self.assertNotRegex(template.subject or "", BRAND_NAME, xmlid)
            self.assertNotRegex(template.body_html or "", BRAND_NAME, xmlid)

    def test_new_user_invitation_links_the_site_of_viindoo(self):
        body = html.fromstring(self.env.ref("auth_signup.set_password_email").with_context(lang="en_US").body_html)
        hosts = {urlsplit(href).hostname for href in body.xpath("//a/@href") if href.startswith("http")}
        self.assertEqual(hosts, {"viindoo.com"})

    def test_password_reset_email_body_names_no_odoo(self):
        arch = self.env.ref("auth_signup.reset_password_email")._get_combined_arch()
        shown = " ".join(arch.xpath("//text()")) + " ".join(arch.xpath("//@href"))
        self.assertNotRegex(shown, BRAND_NAME)

    def _layout_subtitles(self, lang):
        """Return the subtitles the notification layout is rendered with for an account-created email."""
        user = self.env.user
        core_subtitle = LazyTranslate("auth_signup")("Welcome to Odoo")
        rendered = []
        original = IrQweb._render

        def spy(qweb, template, values=None, **options):
            if template == LAYOUT:
                rendered.append(values["subtitles"])
            return original(qweb, template, values, **options)

        with patch.object(IrQweb, "_render", spy):
            self.env["mail.render.mixin"].with_context(
                lang=lang, email_notification_subtitles=[core_subtitle, user.name],
            )._render_encapsulate(LAYOUT, "<p>Body</p>", context_record=user)
        self.assertEqual(len(rendered), 1)
        return rendered[0]

    def test_welcome_subtitle_names_viindoo_in_every_language(self):
        self.env["res.lang"]._activate_lang("vi_VN")
        for lang in ("en_US", "vi_VN"):
            with self.subTest(lang=lang):
                welcome, name = self._layout_subtitles(lang)
                self.assertNotRegex(welcome, BRAND_NAME)
                self.assertIn("Viindoo", welcome)
                self.assertEqual(name, self.env.user.name)

    def test_other_subtitles_are_left_as_they_are(self):
        user = self.env.user
        rendered = []
        original = IrQweb._render

        def spy(qweb, template, values=None, **options):
            if template == LAYOUT:
                rendered.append(values["subtitles"])
            return original(qweb, template, values, **options)

        with patch.object(IrQweb, "_render", spy):
            self.env["mail.render.mixin"].with_context(
                email_notification_subtitles=["Your Account about Odoo", user.name],
            )._render_encapsulate(LAYOUT, "<p>Body</p>", context_record=user)
        self.assertEqual(rendered, [["Your Account about Odoo", user.name]])
