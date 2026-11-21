# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPasskeyDebrand(TransactionCase):

    def test_enrolment_prompt_names_the_relying_party_viindoo(self):
        request = MagicMock()
        request.session = {}

        with patch("odoo.addons.auth_passkey.models.auth_passkey_key.request", request):
            options = self.env["auth.passkey.key"]._start_registration()

        self.assertEqual(options["rp"]["name"], "Viindoo")
