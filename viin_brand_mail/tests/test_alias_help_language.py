import re

from odoo.tests.common import TransactionCase, tagged

ODOO_MARK = re.compile(r'\bOdoo\b|(?i:odoo\.com|odoo@)')
LANG = 'vi_VN'
# The alias fields of the mixin and the field whose help they repeat.
ALIAS_FIELDS = {'alias_name': ('mail.alias', 'alias_name'), 'alias_domain': ('mail.alias.domain', 'name')}


@tagged('post_install', '-at_install')
class TestAliasHelpLanguage(TransactionCase):
    """The alias helps of a model the branding catalog leaves out show no Odoo mark in any language."""

    def _hold_branded_english(self):
        """Give the alias fields of the mixin the English of the fields they repeat.

        A model of a module installed after the branding holds that English; its stock catalog
        translates the stock English of the same helps.
        """
        fields = self.env['ir.model.fields'].search([
            ('model', '=', 'mail.alias.mixin.optional'), ('name', 'in', list(ALIAS_FIELDS)),
        ])
        self.assertEqual(set(fields.mapped('name')), set(ALIAS_FIELDS))
        for field in fields:
            model, name = ALIAS_FIELDS[field.name]
            field.with_context(lang='en_US').help = self.env[model]._fields[name].help
        return fields

    def test_alias_helps_of_a_language_activated_after_the_cluster_have_no_odoo_mark(self):
        fields = self._hold_branded_english()
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(['mail', 'viin_brand_mail'], [LANG])
        for lang in ('en_US', LANG):
            for field in fields:
                with self.subTest(lang=lang, field=field.name):
                    self.assertNotRegex(field.with_context(lang=lang).help or '', ODOO_MARK)
