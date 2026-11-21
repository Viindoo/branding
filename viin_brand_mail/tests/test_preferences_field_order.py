from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPreferencesFieldOrder(TransactionCase):

    def test_color_scheme_follows_the_notification_field_in_preferences(self):
        """The Preferences form lists Color Scheme after the Notification field of mail.

        Views that inherit the same parent apply by priority, then by id, and the id follows module
        load order, so the Color Scheme view carries a priority above mail's.
        """
        view = self.env.ref("base.view_users_form_simple_modif")
        arch = etree.fromstring(self.env["res.users"].get_view(view.id, "form")["arch"])
        names = [field.get("name") for field in arch.xpath("//group[@name='other_preferences']//field")]
        self.assertLess(names.index("notification_type"), names.index("viin_color_scheme"))
