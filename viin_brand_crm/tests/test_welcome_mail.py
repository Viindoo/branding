import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import convert_file
from odoo.tools.translate import get_po_paths, translation_file_reader

# any occurrence of the name: a language may inflect it (Finnish "Odoon")
PRODUCT_NAME = re.compile('odoo', re.IGNORECASE)
WELCOME_XMLID = 'crm.mail_template_demo_crm_lead'
WELCOME_RECORD = 'mail_template_demo_crm_lead'


def _core_catalog_bodies(lang):
    """Return the terms of the welcome mail the stock catalog of ``crm`` translates in ``lang``."""
    terms = []
    for path in get_po_paths('crm', lang):
        with open(path, 'rb') as po_file:
            for row in translation_file_reader(po_file, 'po'):
                if row['module'] == 'crm' and row.get('imd_name') == WELCOME_RECORD and row['value']:
                    terms.append(row['value'])
    return terms


@tagged('post_install', '-at_install')
class TestWelcomeMailOfTheLeads(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.env.ref(WELCOME_XMLID, raise_if_not_found=False):
            # the welcome mail is demo data of crm: a database without demo data loads it for the test
            convert_file(cls.env, 'crm', 'data/mail_template_demo.xml', None, mode='init', noupdate=True)
        cls.template = cls.env.ref(WELCOME_XMLID)
        cls.lead = cls.env['crm.lead'].create({'name': 'Welcome lead'})
        langs = cls.env['res.lang'].with_context(active_test=False).search([])
        cls.stock_langs_naming_the_product = []
        seen = set()
        for code in langs.mapped('code'):
            paths = tuple(get_po_paths('crm', code))
            if paths in seen:
                continue
            seen.add(paths)
            if any(PRODUCT_NAME.search(term) for term in _core_catalog_bodies(code)):
                cls.stock_langs_naming_the_product.append(code)

    def _render(self, lang):
        return self.template.with_context(lang=lang)._render_field('body_html', self.lead.ids)[self.lead.id]

    def _load_stock_translation(self, lang):
        self.env['res.lang']._activate_lang(lang)
        self.env['ir.module.module']._load_module_terms(['crm'], [lang])

    def test_the_stock_catalogs_translate_the_welcome_mail_and_still_name_the_product(self):
        self.assertTrue(self.stock_langs_naming_the_product)

    def test_the_welcome_mail_names_no_odoo_in_every_language_whose_stock_translation_names_it(self):
        english = self._render('en_US')
        self.assertNotRegex(english, PRODUCT_NAME)
        for lang in self.stock_langs_naming_the_product:
            with self.subTest(lang=lang):
                self._load_stock_translation(lang)
                self.assertRegex(self.template.with_context(lang=lang).body_html, PRODUCT_NAME)
                rendered = self._render(lang)
                self.assertNotRegex(rendered, PRODUCT_NAME)
                self.assertEqual(rendered, english, 'a language without a branding catalog shows the English mail')

    def test_a_translation_a_user_wrote_is_rendered_as_it_is(self):
        lang = self.stock_langs_naming_the_product[0]
        self._load_stock_translation(lang)
        self.template.update_field_translations('body_html', {lang: '<p>Written by a user</p>'})
        rendered = self._render(lang)
        self.assertIn('Written by a user', rendered)
        self.assertNotRegex(rendered, PRODUCT_NAME)
        self.assertNotEqual(rendered, self._render('en_US'))

    def test_the_english_sentence_of_a_welcome_body_is_worded_without_the_product_in_any_language(self):
        self.env['res.lang']._activate_lang('fr_FR')
        template = self.env['mail.template'].create({
            'name': 'Welcome Demo',
            'model_id': self.env.ref('crm.model_crm_lead').id,
            'body_html': "<p>I'll help you get the most out of Odoo. Could we plan a quick demo soon?</p>",
        })
        for lang in ('en_US', 'fr_FR'):
            with self.subTest(lang=lang):
                body = template.with_context(lang=lang)._render_field('body_html', self.lead.ids)[self.lead.id]
                self.assertNotRegex(body, PRODUCT_NAME)
