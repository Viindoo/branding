import logging

from odoo import models
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)


class ForumForum(models.Model):
    _inherit = 'forum.forum'

    def _set_default_faq_all_langs(self):
        """Render the default FAQ of the forums in every active language.

        ``_set_default_faq`` fills the language of the environment only, and
        writing ``faq`` in another language than en_US rewrites the en_US value
        with the terms the other language did not translate. The en_US FAQ is
        therefore rendered first, then the translation of each of its terms is
        taken from the render in each other language.
        """
        View = self.env['ir.ui.view']
        for forum in self:
            forum.with_context(lang='en_US')._set_default_faq()
            source_terms = self._get_faq_terms(forum.with_context(lang='en_US').faq)
            for code, _name in self.env['res.lang'].get_installed():
                if code == 'en_US':
                    continue
                rendered = View.with_context(lang=code)._render_template(
                    'website_forum.faq_accordion', {'forum': forum}
                )
                terms = self._get_faq_terms(rendered)
                if len(terms) != len(source_terms):
                    _logger.warning(
                        "Default FAQ of forum %s kept in English for %s: "
                        "%s translated terms for %s source terms",
                        forum.id, code, len(terms), len(source_terms),
                    )
                    continue
                forum.update_field_translations(
                    'faq', {code: dict(zip(source_terms, terms))}
                )

    @staticmethod
    def _get_faq_terms(faq):
        terms = []
        html_translate(lambda term: terms.append(term) or term, str(faq))
        return terms
