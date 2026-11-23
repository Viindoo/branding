from lxml import html

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMailPluginDigestTip(TransactionCase):

    def _tip(self):
        return self.env.ref("mail_plugin.digest_tip_mail_plugin").with_context(lang="en_US")

    def test_the_tip_names_viindoo_not_odoo(self):
        tip = self._tip()
        text = " ".join(html.fromstring(tip.tip_description).itertext())
        self.assertIn("Viindoo", tip.name)
        self.assertIn("Viindoo", text)
        self.assertNotIn("Odoo", f"{tip.name} {text}")

    def test_the_tip_sends_no_link_and_no_image_of_the_servers_of_odoo(self):
        tree = html.fromstring(self._tip().tip_description)
        self.assertFalse(tree.xpath("//a/@href"))
        sources = tree.xpath("//img/@src")
        self.assertTrue(sources)
        for source in sources:
            self.assertTrue(source.startswith("/mail_plugin/static/"), source)

    def test_a_digest_offers_the_tip(self):
        user = self.env.ref("base.user_admin")
        tip = self.env.ref("mail_plugin.digest_tip_mail_plugin")
        (self.env["digest.tip"].search([]) - tip).write({"user_ids": [(4, user.id)]})
        digest = self.env["digest.digest"].create({"name": "Tips digest", "user_ids": [(4, user.id)]})
        descriptions = digest._compute_tips(user.company_id, user, tips_count=1, consumed=False)
        self.assertEqual(len(descriptions), 1)
        self.assertIn("Viindoo", descriptions[0])
