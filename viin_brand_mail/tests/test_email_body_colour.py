# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from unittest.mock import patch

from lxml import html
from markupsafe import Markup

from odoo.tests.common import TransactionCase, new_test_user, tagged

COMPANY_COLOUR = '#123456'
ODOO_COLOURS = ('#875A7B', '#714B67', '#008384', '#8A6381', '#BFA8C2', '#9E588B')
# One element per colour of Odoo, once in capitals and once in lower case, so that each form of
# each colour is measured.
STYLED_ELEMENTS = ''.join(
    '<td class="swatch" style="background-color: %s; color: #FFFFFF;">%s</td>' % (colour, label)
    for colour in ODOO_COLOURS
    for label in (colour.upper(), colour.lower())
)
# The colours of Odoo that are not in a `style` attribute are content, not styling.
BODY = (
    '<table><tbody><tr>%s</tr></tbody></table>'
    '<p class="note">The colour of the product was #714B67.</p>'
) % STYLED_ELEMENTS
LANGUAGES = ('en_US', 'vi_VN', 'fr_FR')


def _styles(rendered):
    return html.fromstring('<div>%s</div>' % rendered).xpath('//*[@style]/@style')


@tagged('post_install', '-at_install')
class TestEmailBodyColour(TransactionCase):
    """A body rendered for a record takes the email colour of the company of that record.

    The stored bodies of a template keep the colours of Odoo in every language; the colour of the
    company is applied to the result of the rendering.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env['res.company'].create({
            'name': 'Colour Co',
            'email_secondary_color': COMPANY_COLOUR,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Colour Partner', 'company_id': cls.company.id})
        cls.template = cls.env['mail.template'].create({
            'name': 'Colour template',
            'model_id': cls.env['ir.model']._get_id('res.partner'),
            'body_html': BODY,
        })
        # A language activated after the module was installed holds a body of its own.
        for lang in LANGUAGES[1:]:
            cls.env['res.lang']._activate_lang(lang)
            cls.template.with_context(lang=lang).body_html = BODY.replace('swatch', 'swatch-%s' % lang)
        cls.stored_bodies = {lang: cls.template.with_context(lang=lang).body_html for lang in LANGUAGES}

    def _render(self, lang):
        template = self.template.with_context(lang=lang)
        return template._render_field('body_html', [self.partner.id])[self.partner.id]

    def test_a_template_body_takes_the_company_colour_in_every_language(self):
        for lang in LANGUAGES:
            with self.subTest(lang=lang):
                styles = _styles(self._render(lang))
                self.assertEqual(len(styles), len(ODOO_COLOURS) * 2)
                for style in styles:
                    self.assertIn('background-color: %s' % COMPANY_COLOUR, style)
                    for colour in ODOO_COLOURS:
                        self.assertNotIn(colour.lower(), style.lower())

    def test_the_stored_bodies_are_left_as_they_are(self):
        for lang in LANGUAGES:
            self._render(lang)
        self.template.invalidate_recordset()
        for lang in LANGUAGES:
            with self.subTest(lang=lang):
                stored = self.template.with_context(lang=lang).body_html
                self.assertEqual(stored, self.stored_bodies[lang])
                self.assertIn('#875A7B', stored)

    def test_only_the_style_attributes_are_changed(self):
        rendered = self._render('en_US')
        self.assertIn('The colour of the product was #714B67.', rendered)

    def test_a_company_without_a_colour_gets_the_brand_colour(self):
        self.company.email_secondary_color = False
        styles = _styles(self._render('en_US'))
        self.assertTrue(styles)
        for style in styles:
            self.assertIsNone(re.search('(?i)' + '|'.join(ODOO_COLOURS), style))
            self.assertIn('background-color: #7F4282', style)

    def test_each_record_takes_the_colour_of_its_own_company(self):
        other_company = self.env['res.company'].create({'name': 'Other Co', 'email_secondary_color': '#654321'})
        other_partner = self.env['res.partner'].create({'name': 'Other Partner', 'company_id': other_company.id})
        rendered = self.template._render_field('body_html', [self.partner.id, other_partner.id])
        self.assertIn('background-color: %s' % COMPANY_COLOUR, rendered[self.partner.id])
        self.assertIn('background-color: #654321', rendered[other_partner.id])
        self.assertNotIn(COMPANY_COLOUR, rendered[other_partner.id])

    def test_a_composer_body_takes_the_company_colour(self):
        composer = self.env['mail.compose.message'].create({
            'composition_mode': 'mass_mail',
            'model': 'res.partner',
            'res_ids': repr([self.partner.id]),
            'body': BODY,
        })
        rendered = composer._render_field('body', [self.partner.id])[self.partner.id]
        styles = _styles(rendered)
        self.assertTrue(styles)
        for style in styles:
            self.assertRegex(style, r'background-color:\s*%s' % COMPANY_COLOUR)
            self.assertIsNone(re.search('(?i)' + '|'.join(ODOO_COLOURS), style))

    def test_the_rendered_markup_stays_markup_and_only_the_colours_change(self):
        """A caller that wraps the result of the postprocess (a renamed product in another module)
        gets back the same type, so the two overrides compose in either order."""
        body = Markup('<p style="color: #875A7B">Hello <b>World</b> #875A7B</p>')
        rendered = self.env['mail.render.mixin']._render_template_postprocess(
            'res.partner', {self.partner.id: body},
        )[self.partner.id]
        self.assertIsInstance(rendered, Markup)
        self.assertEqual(
            rendered, Markup('<p style="color: %s">Hello <b>World</b> #875A7B</p>' % COMPANY_COLOUR),
        )


@tagged('post_install', '-at_install')
class TestSecurityAlertColour(TransactionCase):
    """The security email of mail (`mail.account_security_alert`) carries its button colour in the
    template and is rendered through the same postprocess, so it takes the company colour too."""

    def test_the_reset_password_button_takes_the_company_colour_in_every_language(self):
        # sudo: arrange - the system parameter is not readable or writable by the test user
        self.env['ir.config_parameter'].sudo().set_bool('auth_signup.reset_password', True)
        company = self.env['res.company'].create({'name': 'Alert Co', 'email_secondary_color': COMPANY_COLOUR})
        user = new_test_user(
            self.env, login='security_alert_user', groups='base.group_user',
            company_id=company.id, company_ids=[(6, 0, company.ids)],
        )
        for lang in LANGUAGES:
            self.env['res.lang']._activate_lang(lang)
            user.lang = lang
            with self.subTest(lang=lang):
                # the email is only queued here: nothing is sent
                with patch.object(self.env.registry['mail.mail'], 'send', return_value=True):
                    mails = user._notify_security_setting_update(
                        'Security update', 'Your password has changed.', suggest_password_reset=True,
                    )
                tree = html.fromstring(mails.body_html)
                buttons = tree.xpath('//a[contains(@href, "/web/reset_password")]')
                self.assertEqual(len(buttons), 1)
                style = buttons[0].get('style')
                self.assertIn(COMPANY_COLOUR, style)
                self.assertNotIn('#875A7B', style.upper())
