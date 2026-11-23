import re
from urllib.parse import urlsplit

from lxml import html

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_path

COMPANY_COLOUR = '#123456'


@tagged('post_install', '-at_install')
class TestDigestBranding(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.user
        cls.user.company_id.email_secondary_color = COMPANY_COLOUR
        cls.digest = cls.env['digest.digest'].create({
            'name': 'Branding digest',
            'user_ids': [(4, cls.user.id)],
            'kpi_res_users_connected': True,
            'kpi_mail_message_total': True,
        })

    def _send(self):
        """Return the parsed body of the email the digest sends to the current user."""
        self.digest._action_send_to_user(self.user)
        mail = self.env['mail.mail'].search([('subject', 'like', 'Branding digest')], order='id desc', limit=1)
        self.assertTrue(mail)
        return mail.body_html, html.fromstring(mail.body_html)

    def test_the_icon_of_a_kpi_is_a_path_that_exists_in_this_database(self):
        kpis = self.digest._compute_kpis(self.user.company_id, self.user)
        self.assertTrue(kpis)
        for kpi in kpis:
            with self.subTest(kpi=kpi['kpi_name']):
                icon = urlsplit(kpi['kpi_icon'])
                self.assertFalse(icon.netloc)
                self.assertTrue(file_path(icon.path.lstrip('/')))

    def test_the_icons_of_the_email_are_served_by_the_database(self):
        _body, tree = self._send()
        icons = tree.xpath('//img[contains(@class, "kpi_header_icon")]/@src')
        self.assertTrue(icons)
        database_host = urlsplit(self.digest.get_base_url()).netloc
        for icon in icons:
            self.assertEqual(urlsplit(icon).netloc, database_host)

    def test_the_powered_by_link_takes_the_company_colour(self):
        body, tree = self._send()
        label = tree.xpath('//p[@id="powered"]//span[contains(@class, "odoo_link_text")]')[0]
        self.assertNotIn('color', label.get('style') or '')
        rule = re.search(r'\.odoo_link_text\s*\{[^}]*?[^-]color:\s*(#[0-9a-fA-F]{6})', body)
        self.assertEqual(rule.group(1).lower(), COMPANY_COLOUR)

    def test_no_image_of_the_email_is_loaded_from_the_servers_of_odoo(self):
        _body, tree = self._send()
        sources = tree.xpath('//img/@src')
        self.assertTrue(sources)
        for source in sources:
            with self.subTest(source=source):
                self.assertNotRegex(urlsplit(source).netloc, r'(^|\.)odoo(cdn)?\.com$')
        badges = tree.xpath('//img[contains(@class, "download_app")]/@src')
        self.assertEqual(len(badges), 2)
        database_host = urlsplit(self.digest.get_base_url()).netloc
        for badge in badges:
            self.assertEqual(urlsplit(badge).netloc, database_host)

    def test_a_company_without_a_colour_gets_the_brand_colour_in_the_digest_style(self):
        self.user.company_id.email_secondary_color = False
        body, _tree = self._send()
        self.assertIn('#7F4282', body)
        self.assertNotIn('#714B67', body.upper())

    def test_the_email_names_viindoo_in_its_links_and_text(self):
        _body, tree = self._send()
        for link in tree.xpath('//a/@href'):
            self.assertNotRegex(urlsplit(link).netloc, r'(^|\.)odoo\.com$')
        text = ' '.join(tree.xpath('//body//text()'))
        self.assertNotIn('Odoo', text)
        self.assertIn('Viindoo', ' '.join(tree.xpath('//p[@id="powered"]//text()')))

    def test_the_tips_that_name_the_product_name_viindoo(self):
        for xmlid in ('digest.digest_tip_digest_0', 'digest.digest_tip_digest_2', 'digest.digest_tip_digest_3'):
            with self.subTest(tip=xmlid):
                tip = self.env.ref(xmlid)
                self.assertNotRegex(f'{tip.name} {tip.tip_description}', r'(?i)odoo')
        tip = self.env.ref('digest.digest_tip_digest_3')
        self.assertIn('@ViindooBot', tip.tip_description)
        self.assertTrue(html.fromstring(tip.tip_description).xpath('//img/@src'))

    def test_no_stored_tip_of_a_core_module_that_has_a_branding_module_names_odoo(self):
        branded = {
            name.removeprefix('viin_brand_')
            for name in self.env['ir.module.module'].search([
                ('state', '=', 'installed'), ('name', '=like', 'viin\\_brand\\_%'),
            ]).mapped('name')
        }
        data = self.env['ir.model.data'].search([('model', '=', 'digest.tip'), ('module', 'in', list(branded))])
        tips = self.env['digest.tip'].with_context(active_test=False).browse(data.mapped('res_id'))
        self.assertTrue(tips)
        for tip in tips:
            tip = tip.with_context(lang='en_US')
            text = ' '.join(html.fromstring(tip.tip_description).itertext())
            with self.subTest(tip=tip.name):
                self.assertNotRegex(f'{tip.name} {text}', r'(?i)odoo')

    def test_a_tip_can_be_archived(self):
        tip = self.env.ref('digest.digest_tip_digest_1')
        tip.active = False
        self.assertNotIn(tip, self.env['digest.tip'].search([]))
        self.assertIn(tip, self.env['digest.tip'].with_context(active_test=False).search([]))


@tagged('post_install', '-at_install')
class TestDigestTipSelection(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_admin')
        # the tips already shipped are consumed, so that only the two tips below are pending
        cls.env['digest.tip'].search([]).write({'user_ids': [(4, cls.user.id)]})
        group = cls.env.ref('base.group_user')
        tips = cls.env['digest.tip']
        cls.odoo_image_tip = tips.create({
            'name': 'Tip with an Odoo screenshot',
            'sequence': 1,
            'group_id': group.id,
            'tip_description': '<div><p>With picture</p>'
                               '<img src="https://download.odoocdn.com/digests/digest/static/src/img/x.gif"/></div>',
        })
        cls.plain_tip = tips.create({
            'name': 'Plain tip',
            'sequence': 2,
            'group_id': group.id,
            'tip_description': '<div><p>Plain words</p><img src="/digest/static/src/img/milk-calculator.gif"/></div>',
        })
        cls.digest = cls.env['digest.digest'].create({'name': 'Tips digest', 'user_ids': [(4, cls.user.id)]})

    def test_a_digest_never_sends_a_tip_that_loads_an_image_from_the_servers_of_odoo(self):
        descriptions = self.digest._compute_tips(self.user.company_id, self.user, tips_count=1)
        self.assertEqual(len(descriptions), 1)
        self.assertIn('Plain words', descriptions[0])
        self.assertNotIn('odoocdn', descriptions[0])

    def test_the_tip_with_an_odoo_image_stays_pending_and_the_plain_one_is_consumed(self):
        self.digest._compute_tips(self.user.company_id, self.user, tips_count=2)
        self.assertIn(self.user, self.plain_tip.user_ids)
        self.assertNotIn(self.user, self.odoo_image_tip.user_ids)

    def test_a_search_outside_the_digest_still_finds_every_tip(self):
        tips = self.env['digest.tip'].search([('id', 'in', (self.odoo_image_tip | self.plain_tip).ids)])
        self.assertEqual(tips, self.odoo_image_tip | self.plain_tip)

    def test_a_translated_tip_is_selected_by_the_same_rule(self):
        self.env['res.lang']._activate_lang('fr_FR')
        self.user.lang = 'fr_FR'
        self.odoo_image_tip.with_context(lang='fr_FR').tip_description = (
            '<div><p>Avec image</p>'
            '<img src="https://download.odoocdn.com/digests/digest/static/src/img/x.gif"/></div>'
        )
        descriptions = self.digest.with_context(lang='fr_FR')._compute_tips(
            self.user.company_id, self.user, tips_count=1,
        )
        self.assertEqual(len(descriptions), 1)
        self.assertIn('Plain words', descriptions[0])
