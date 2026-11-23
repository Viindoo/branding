import re

from odoo import api, models

# The sentence of the welcome mail of the demo leads that names the product, and its replacement.
PRODUCT_SENTENCE = 'get the most out of Odoo'
BRAND_SENTENCE = 'get the most out of our solutions'
WELCOME_TEMPLATE_XMLID = 'crm.mail_template_demo_crm_lead'
PRODUCT_NAME = re.compile('odoo', re.IGNORECASE)


class MailRenderMixin(models.AbstractModel):
    _inherit = 'mail.render.mixin'

    @api.model
    def _render_template_postprocess(self, model, rendered):
        """Take the product name out of the welcome mail of the demo leads.

        The mail template keeps one body per language, so the sentence is replaced in the result of
        the rendering, which every language goes through; the stored bodies are left as they are.

        :param str model: model of the records the bodies were rendered on
        :param dict rendered: ``{res_id: rendered body}``
        :return: ``rendered``, with the sentence replaced in the bodies rendered on leads
        """
        rendered = super()._render_template_postprocess(model, rendered)
        if model != 'crm.lead':
            return rendered
        for res_id, body in rendered.items():
            if isinstance(body, str) and PRODUCT_SENTENCE in body:
                rendered[res_id] = body.__class__(body.replace(PRODUCT_SENTENCE, BRAND_SENTENCE))
        return rendered

    @api.model
    def _render_template(self, template_src, model, res_ids, engine='inline_template',
                         add_context=None, options=None):
        """Render the welcome mail of the demo leads in English where its translation names the product.

        The sentence naming the product is worded by the catalog of each language, so it is not
        found by its English text. The catalogs of the branding modules word it without the
        product; where the language has none, the stock translation still names it, and the
        English body, which the post-processing words without the product, is rendered instead.
        A translation that no longer names the product is rendered as it is.

        :param str template_src: the body of the template, in the language the template is read in
        :return: ``{res_id: rendered body}``
        """
        template_src = self._get_welcome_body_without_product(template_src)
        return super()._render_template(
            template_src, model, res_ids, engine=engine, add_context=add_context, options=options)

    def _get_welcome_body_without_product(self, template_src):
        """Return the body to render: the English one where the translated welcome body names the product.

        :param str template_src: the body of the template, in the language the template is read in
        :return: ``template_src``, or the English body of the welcome template
        """
        lang = self.env.lang
        if (
            self._name != 'mail.template'
            or not lang
            or lang == 'en_US'
            or not isinstance(template_src, str)
            or not PRODUCT_NAME.search(template_src)
        ):
            return template_src
        welcome = self.env.ref(WELCOME_TEMPLATE_XMLID, raise_if_not_found=False)
        if not welcome or self != welcome or template_src != self.body_html:
            return template_src
        return self.with_context(lang='en_US').body_html
