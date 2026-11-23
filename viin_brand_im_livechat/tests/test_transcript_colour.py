# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo import Command
from odoo.tests.common import TransactionCase, tagged

COMPANY_COLOUR = '#123456'
LEGACY_PURPLES = ('#875a7b', '#714b67')


@tagged('post_install', '-at_install')
class TestTranscriptColour(TransactionCase):
    """The conversation copy a visitor receives is painted with the colours of the company."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('vi_VN')
        cls.company = cls.env.company
        cls.company.email_secondary_color = COMPANY_COLOUR
        cls.operator = cls.env['res.users'].create({
            'name': 'Transcript Operator',
            'login': 'transcript_operator',
            'email': 'transcript.operator@example.com',
            'group_ids': [Command.link(cls.env.ref('im_livechat.im_livechat_group_user').id)],
        })
        cls.livechat = cls.env['im_livechat.channel'].create({
            'name': 'Transcript channel',
            'header_background_color': False,
        })

    def _transcript_body(self, lang):
        channel = self.env['discuss.channel'].create({
            'name': 'Visitor',
            'channel_type': 'livechat',
            'livechat_channel_id': self.livechat.id,
            'channel_member_ids': [Command.create({'partner_id': self.operator.partner_id.id})],
        })
        attachment = self.env['ir.attachment'].create({
            'name': 'notes.txt',
            'raw': b'notes',
            'mimetype': 'text/plain',
            'res_model': 'discuss.channel',
            'res_id': channel.id,
        })
        channel.with_user(self.operator).message_post(
            body='Here are my notes', message_type='comment', subtype_xmlid='mail.mt_comment',
            attachment_ids=attachment.ids,
        )
        channel.with_context(lang=lang)._email_livechat_transcript('visitor@example.com')
        mail = self.env['mail.mail'].search([('email_to', '=', 'visitor@example.com')], order='id desc', limit=1)
        self.assertTrue(mail)
        return html.fromstring(mail.body)

    def test_the_attachment_tag_takes_the_company_colour_in_every_language(self):
        for lang in ('en_US', 'vi_VN'):
            with self.subTest(lang=lang):
                tree = self._transcript_body(lang)
                tag = tree.xpath('//strong[normalize-space()="text/plain"]')[0]
                self.assertIn('background-color:%s' % COMPANY_COLOUR, tag.get('style').replace(' ', ''))
                body = html.tostring(tree).decode().lower()
                for colour in LEGACY_PURPLES:
                    self.assertNotIn(colour, body)

    def test_the_names_take_the_company_colour_when_the_channel_names_none(self):
        for lang in ('en_US', 'vi_VN'):
            with self.subTest(lang=lang):
                tree = self._transcript_body(lang)
                name = tree.xpath('//strong[normalize-space()="Transcript Operator"]')[0]
                self.assertIn('color:%s' % COMPANY_COLOUR, name.get('style').replace(' ', ''))

    def test_a_channel_colour_wins_over_the_company_colour_for_the_names(self):
        self.livechat.header_background_color = '#00AA55'
        tree = self._transcript_body('en_US')
        name = tree.xpath('//strong[normalize-space()="Transcript Operator"]')[0]
        self.assertIn('color:#00AA55', name.get('style').replace(' ', ''))
