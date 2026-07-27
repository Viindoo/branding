# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerRootDebrand(TransactionCase):
    """The built-in bot partner must carry Viindoo branding, not Odoo branding.

    ``data/res_partner_data.xml`` re-brands ``base.partner_root`` (the author of
    every system-generated message) from OdooBot to ViindooBot. That record is
    highly visible - it is the author shown on automated chatter messages - so the
    de-brand is a shipped product behaviour and must be protected.

    This assertion was previously impossible to make: ``post_init_hook`` used to
    write the record back to ``OdooBot`` / ``odoobot@example.com`` whenever
    ``test_enable`` was set, so under the test runner the module's own de-brand was
    never observable. That fixture write now lives in a rollback-safe test setup
    (see ``post_load`` in this module's ``__init__.py``), scoped to the core suites
    that genuinely need core's naming, which leaves the real committed value
    de-branded and therefore testable here.

    Note this case deliberately derives from a plain ``TransactionCase`` rather than
    ``mail.tests.common.MailCommon``: the fixture above restores core's OdooBot
    naming for ``MailCommon`` subclasses, so asserting the de-brand there would
    observe the fixture instead of the product.
    """

    def test_partner_root_is_viindoo_branded(self):
        partner_root = self.env.ref("base.partner_root")
        self.assertEqual(
            partner_root.name,
            "ViindooBot",
            "base.partner_root must be de-branded to ViindooBot - it is the "
            "visible author of system-generated chatter messages",
        )
        self.assertEqual(
            partner_root.email,
            "viindoobot@example.viindoo.com",
            "base.partner_root must not keep the Odoo example.com bot address",
        )
