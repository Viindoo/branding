# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNotificationLayoutDebrand(TransactionCase):
    """The notification email layout footer must be Viindoo-branded, not Odoo.

    ``viin_brand_mail`` inherits ``mail.mail_notification_layout`` and
    ``mail.mail_notification_light`` to replace the trailing "Powered by Odoo"
    wordmark with "Viindoo" and re-point its marketing link to
    ``https://viindoo.com?utm_source=db&utm_medium=email``.

    These tests exercise the real mail render path
    (``mail.render.mixin._render_encapsulate`` -> ``ir.qweb._render``, the exact
    call Odoo uses in ``mail_thread._notify_by_email_render_layout``) and assert
    the de-branded outcome on the PRODUCED HTML - never on template internals -
    so a correct de-brand passes regardless of which XPath achieves it, and a
    layout still carrying the Odoo wordmark / odoo.com link fails.

    The neutral notification body below contains neither ``Viindoo`` nor
    ``odoo.com``, so every assertion can be satisfied (or broken) only by the
    layout de-brand itself.
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
