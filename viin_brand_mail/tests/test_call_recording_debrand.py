# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo import fields
from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestCallRecordingEmailDebrand(TransactionCase):
    """The email that announces a meeting recording names Viindoo in the language of its recipient."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env['discuss.channel'].create({'name': 'Recorded call', 'channel_type': 'group'})
        cls.env['res.lang']._activate_lang('fr_FR')

    def _send_recording_email(self, lang):
        starter = new_test_user(self.env, login='recorder_%s' % lang, groups='base.group_user')
        starter.partner_id.lang = lang
        call = self.env['discuss.call.history'].create({
            'channel_id': self.channel.id,
            'start_dt': fields.Datetime.now(),
        })
        artifact = self.env['mail.call.artifact'].create({
            'discuss_call_history_id': call.id,
            'recording_started_by_id': starter.id,
            'start_ms': 0,
            'end_ms': 1000,
        })
        self.env['ir.attachment'].create({
            'name': 'recording.webm',
            'res_model': artifact._name,
            'res_id': artifact.id,
            'mimetype': 'video/webm',
            'raw': b'recording',
        })
        artifact.invalidate_recordset(['media_id'])
        artifact._send_recording_available_email()
        mail = self.env['mail.mail'].search([('model', '=', artifact._name), ('res_id', '=', artifact.id)])
        self.assertEqual(len(mail), 1)
        return mail

    def test_the_email_names_viindoo_not_odoo_whatever_the_language_of_the_recipient(self):
        for lang in ('en_US', 'fr_FR'):
            with self.subTest(lang=lang):
                text = html.fromstring(self._send_recording_email(lang).body_html).text_content()
                self.assertIn('Viindoo', text)
                self.assertNotIn('Odoo', text)
