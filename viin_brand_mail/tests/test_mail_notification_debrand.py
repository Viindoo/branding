# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNotificationLayoutDebrand(TransactionCase):
    """The notification email layout footer is Viindoo-branded, not Odoo.

    The "Powered by Odoo" wordmark of ``mail.mail_notification_layout`` and
    ``mail.mail_notification_light`` reads "Viindoo" and links to
    ``https://viindoo.com?utm_source=db&utm_medium=email``. The assertions run on the HTML rendered
    from a neutral body that contains neither ``Viindoo`` nor ``odoo.com``.
    """

    _NEUTRAL_BODY = "<p>Notification body used for branding assertions.</p>"

    def _render_layout(self, layout_xmlid, add_context=None):
        rendered = self.env["mail.render.mixin"]._render_encapsulate(
            layout_xmlid,
            self._NEUTRAL_BODY,
            add_context=add_context or {},
        )
        return str(rendered)

    def test_notification_layout_footer_shows_viindoo_not_odoo(self):
        # Force the footer block on so the trailing "Powered by" wordmark renders.
        rendered = self._render_layout(
            "mail.mail_notification_layout",
            add_context={"email_notification_force_footer": True},
        )
        self.assertIn(
            "viindoo.com",
            rendered,
            "Notification layout footer link must point to viindoo.com",
        )
        self.assertIn(
            "Viindoo",
            rendered,
            "Notification layout footer wordmark must read 'Viindoo'",
        )
        self.assertNotIn(
            "odoo.com",
            rendered,
            "Notification layout footer must not keep a live odoo.com marketing link",
        )

    def test_notification_light_footer_shows_viindoo_not_odoo(self):
        # The light layout renders its "Powered by" footer unconditionally.
        rendered = self._render_layout("mail.mail_notification_light")
        self.assertIn(
            "viindoo.com",
            rendered,
            "Light notification footer link must point to viindoo.com",
        )
        self.assertIn(
            "Viindoo",
            rendered,
            "Light notification footer wordmark must read 'Viindoo'",
        )
        self.assertNotIn(
            "odoo.com",
            rendered,
            "Light notification footer must not keep a live odoo.com marketing link",
        )
