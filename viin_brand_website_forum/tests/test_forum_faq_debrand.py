# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo.addons.viin_brand_website_forum import post_init_hook
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestForumFaqDebrand(HttpCase):
    """The help pages of a forum (default FAQ and karma page) name Viindoo
    and never Odoo.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.forum = cls.env["forum.forum"].create({"name": "Brand Forum"})
        vi_lang = cls.env["res.lang"]._activate_lang("vi_VN")
        cls.env["ir.module.module"]._load_module_terms(
            ["website_forum", "viin_brand_website_forum"], ["vi_VN"], overwrite=True
        )
        cls.env["website"].search([]).language_ids |= vi_lang
        cls.vi_env = cls.env(context=dict(cls.env.context, lang="vi_VN"))

    def test_default_faq_of_new_forum_has_no_odoo_word(self):
        faq = html.fromstring(self.forum.faq).text_content()
        self.assertNotIn("Odoo", faq, "The default FAQ must not mention Odoo")
        self.assertIn(
            "questions related to Viindoo",
            faq,
            "The default FAQ must name Viindoo as the community subject",
        )

    def test_faq_karma_page_has_no_odoo_word(self):
        response = self.url_open("/forum/%s/faq/karma" % self.forum.id)
        self.assertEqual(response.status_code, 200)
        karma_cards = html.fromstring(response.content).xpath(
            "//div[@data-name='Item']"
        )
        self.assertTrue(karma_cards, "The karma page must render its help card")
        card_text = "".join(card.text_content() for card in karma_cards)
        self.assertNotIn("Odoo", card_text, "The karma page must not mention Odoo")
        self.assertIn(
            "questions related to Viindoo",
            card_text,
            "The karma page must name Viindoo as the community subject",
        )

    def test_new_forum_created_in_vietnamese_has_viindoo_faq(self):
        forum = self.vi_env["forum.forum"].create({"name": "Diễn đàn thương hiệu"})
        faq = html.fromstring(forum.faq).text_content()
        self.assertNotIn("Odoo", faq, "The Vietnamese FAQ must not mention Odoo")
        self.assertIn(
            "liên quan tới Viindoo", faq, "The Vietnamese FAQ must name Viindoo"
        )

    def test_faq_karma_page_renders_in_vietnamese_without_odoo_word(self):
        response = self.url_open("/vi/forum/%s/faq/karma" % self.forum.id)
        self.assertEqual(response.status_code, 200)
        card_text = "".join(
            card.text_content()
            for card in html.fromstring(response.content).xpath(
                "//div[@data-name='Item']"
            )
        )
        self.assertTrue(card_text, "The Vietnamese karma page must render its card")
        self.assertNotIn("Odoo", card_text, "The karma page must not mention Odoo")
        self.assertIn("Viindoo", card_text, "The karma page must name Viindoo")

    def _assert_faq_in_each_language(self, forum):
        for lang, phrase, other_phrase in (
            ("en_US", "questions related to Viindoo", "liên quan tới Viindoo"),
            ("vi_VN", "liên quan tới Viindoo", "questions related to Viindoo"),
        ):
            faq = html.fromstring(forum.with_context(lang=lang).faq).text_content()
            self.assertNotIn("Odoo", faq, "The %s FAQ must not mention Odoo" % lang)
            self.assertIn(phrase, faq, "The %s FAQ must be in %s" % (lang, lang))
            self.assertNotIn(
                other_phrase, faq, "The %s FAQ must be in %s" % (lang, lang)
            )

    def test_default_faq_reset_covers_every_active_language(self):
        odoo_faq = "<p>Odoo FAQ</p>"
        self.forum.with_context(lang="en_US").faq = odoo_faq
        self.forum.with_context(lang="vi_VN").faq = odoo_faq

        self.forum._set_default_faq_all_langs()

        self._assert_faq_in_each_language(self.forum)

    def test_install_hook_rebrands_the_faq_of_the_help_forum_in_every_language(self):
        forum_help = self.env.ref("website_forum.forum_help")
        odoo_faq = "<p>Odoo FAQ</p>"
        forum_help.with_context(lang="en_US").faq = odoo_faq
        forum_help.with_context(lang="vi_VN").faq = odoo_faq

        post_init_hook(self.env)

        self._assert_faq_in_each_language(forum_help)
