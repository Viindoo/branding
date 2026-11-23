# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand_website_slides_forum import post_init_hook


@tagged("post_install", "-at_install")
class TestSlidesForumFaq(TransactionCase):
    """The forums of the eLearning sample courses show the Viindoo FAQ and
    never the Odoo one.
    """

    DEMO_FORUM_NAMES = ("forum_forum_demo_channel_0", "forum_forum_demo_channel_2")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The xmlids of the sample forums exist only with demo data: forge them in
        # this rolled-back transaction so the hook's lookup is exercised either way.
        cls.forums = cls.env["forum.forum"]
        for name in cls.DEMO_FORUM_NAMES:
            forum = cls.env.ref("website_slides_forum." + name, raise_if_not_found=False)
            if not forum:
                forum = cls.env["forum.forum"].create({"name": name})
                cls.env["ir.model.data"].create(
                    {
                        "module": "website_slides_forum",
                        "name": name,
                        "model": "forum.forum",
                        "res_id": forum.id,
                    }
                )
            cls.forums |= forum
        cls.env["res.lang"]._activate_lang("vi_VN")
        cls.env["ir.module.module"]._load_module_terms(
            ["website_forum", "viin_brand_website_forum"], ["vi_VN"], overwrite=True
        )

    def _faq_text(self, forum, lang):
        return html.fromstring(forum.with_context(lang=lang).faq).text_content()

    def test_install_hook_rebrands_course_forums_in_every_language(self):
        for forum in self.forums:
            forum.with_context(lang="en_US").faq = "<p>Odoo FAQ</p>"
            forum.with_context(lang="vi_VN").faq = "<p>Odoo FAQ</p>"

        post_init_hook(self.env)

        for forum in self.forums:
            faqs = {lang: self._faq_text(forum, lang) for lang in ("en_US", "vi_VN")}
            for lang, faq in faqs.items():
                self.assertNotIn("Odoo", faq, "%s FAQ (%s)" % (forum.name, lang))
                self.assertIn("Viindoo", faq, "%s FAQ (%s)" % (forum.name, lang))
            self.assertNotEqual(
                faqs["vi_VN"], faqs["en_US"], "%s FAQ must be translated" % forum.name
            )
