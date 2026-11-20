# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from lxml import etree, html

from odoo.tests.common import TransactionCase, tagged

# Arabic: the core catalog words the disclaimer without the Latin product name.
LANG = 'ar_001'


@tagged('post_install', '-at_install')
class TestDefaultTermsTemplate(TransactionCase):

    def _disclaimer(self, xmlid, lang, index):
        """Return the text of a paragraph of a template's own arch in a language."""
        arch = self.env.ref(xmlid).with_context(lang=lang).arch
        return etree.fromstring(arch).xpath('//p')[index].text

    def _default_terms_paragraphs(self, lang):
        """Switch the company to terms on a web page in a language, as its settings do."""
        company = self.env.company.with_context(lang=lang)
        company.write({'terms_type': 'plain', 'invoice_terms_html': False})
        company.terms_type = 'html'
        self.assertTrue(company.invoice_terms_html, 'the default terms are rendered')
        return [p.text_content() for p in html.fromstring(company.invoice_terms_html).iter('p')]

    def test_default_terms_carry_the_viindoo_disclaimer_in_every_language(self):
        """The disclaimer is replaced by its place in the template, whatever the language."""
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(['account', 'viin_brand_account'], [LANG])
        core = 'account.account_default_terms_and_conditions'
        brand = 'viin_brand_account.account_default_terms_and_conditions'
        core_disclaimer = self._disclaimer(core, LANG, 1)
        self.assertNotIn('Odoo', core_disclaimer, 'a translation without the product name expected')
        for lang in ('en_US', LANG):
            with self.subTest(lang=lang):
                paragraphs = self._default_terms_paragraphs(lang)
                self.assertIn(self._disclaimer(brand, lang, 0), paragraphs)
                self.assertNotIn(self._disclaimer(core, lang, 1), paragraphs)
                self.assertEqual(len(paragraphs), 2)
        self.assertIn("Viindoo's responsibility", self._disclaimer(brand, 'en_US', 0))
