import re

from odoo import api, models

# The logo that the e-invoice notification mails of core show in their header, and the one that
# replaces it.
CORE_LOGO_PATH = '/web/static/img/logo_inverse_white_206px.png'
BRAND_LOGO_PATH = '/viin_brand/static/img/Viindoo-logo-inverted.svg'
# The models of the e-invoice notification templates.
EINVOICE_NOTIFICATION_MODELS = ('account.journal', 'account.move')

_CORE_LOGO_TAG_RE = re.compile(r'<img\b[^>]*?%s[^>]*>' % re.escape(CORE_LOGO_PATH), re.IGNORECASE)
_ALT_RE = re.compile(r'''\balt\s*=\s*(?:"Odoo"|'Odoo')''', re.IGNORECASE)


def _brand_logo_tag(tag):
    """Return the image tag ``tag`` of the core logo with the logo of Viindoo in its place."""
    return _ALT_RE.sub('alt="Viindoo"', tag.group().replace(CORE_LOGO_PATH, BRAND_LOGO_PATH))


class MailRenderMixin(models.AbstractModel):
    _inherit = 'mail.render.mixin'

    @api.model
    def _render_template_postprocess(self, model, rendered):
        """Show the logo of Viindoo in the header of the e-invoice notification mails.

        The mail templates keep one body per language, and a language activated later brings its
        own, so the logo is replaced in the result of the rendering, which every language goes
        through; the stored bodies are left as they are.

        :param str model: model of the records the bodies were rendered on
        :param dict rendered: ``{res_id: rendered body}``
        :return: ``rendered``, with the logo of Odoo replaced in the e-invoice notification mails
        """
        rendered = super()._render_template_postprocess(model, rendered)
        if model not in EINVOICE_NOTIFICATION_MODELS:
            return rendered
        for res_id, body in rendered.items():
            if isinstance(body, str) and CORE_LOGO_PATH in body:
                rendered[res_id] = body.__class__(_CORE_LOGO_TAG_RE.sub(_brand_logo_tag, body))
        return rendered
