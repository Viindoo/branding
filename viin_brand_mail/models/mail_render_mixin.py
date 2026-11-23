import re

from markupsafe import escape

from odoo import api, models

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

# The colours that the email templates of Odoo paint in the `style` of their buttons, headers and
# links. Each one is a colour of the product, so an email takes the colour of the company instead.
ODOO_EMAIL_COLOURS = ('#875A7B', '#714B67', '#008384', '#8A6381', '#BFA8C2', '#9E588B')

_ODOO_COLOUR_RE = re.compile('|'.join(ODOO_EMAIL_COLOURS), re.IGNORECASE)
_STYLE_ATTRIBUTE_RE = re.compile(r'''(?<![\w-])style\s*=\s*(?:"[^"]*"|'[^']*')''', re.IGNORECASE)


def _recolour_styles(body, colour):
    """Return ``body`` with the colours of Odoo replaced by ``colour`` in its `style` attributes."""
    return body.__class__(_STYLE_ATTRIBUTE_RE.sub(
        lambda style: _ODOO_COLOUR_RE.sub(lambda _odoo_colour: colour, style.group()),
        body,
    ))


class MailRenderMixin(models.AbstractModel):
    _inherit = 'mail.render.mixin'

    @api.model
    def _render_template_postprocess(self, model, rendered):
        """Give every rendered body the email colour of the company of its record.

        The bodies of the mail templates, of the composer and of the mailings are stored with the
        colours of Odoo in the `style` attribute of their markup, one body per language, and a
        language activated later brings its own bodies. The colours are therefore replaced in the
        result of the rendering, which every language and every template goes through; the stored
        bodies are left as they are.

        :param str model: model of the records the bodies were rendered on
        :param dict rendered: ``{res_id: rendered body}``
        :return: ``rendered``, with the colours of Odoo replaced in the `style` attributes
        """
        rendered = super()._render_template_postprocess(model, rendered)
        res_ids = [
            res_id for res_id, body in rendered.items()
            if isinstance(body, str) and _ODOO_COLOUR_RE.search(body)
        ]
        if not res_ids:
            return rendered
        records = self.env[model].browse([res_id for res_id in res_ids if res_id]) if model else None
        companies = records._mail_get_companies(default=self.env.company) if records else {}
        for res_id in res_ids:
            company = companies.get(res_id) or self.env.company
            colour = str(escape(company.email_secondary_color or VIINDOO_BRAND_COLOR))
            rendered[res_id] = _recolour_styles(rendered[res_id], colour)
        return rendered
