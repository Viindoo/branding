from markupsafe import Markup

from odoo import models


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    @classmethod
    def _get_style_dict(cls):
        style_dict = super()._get_style_dict()
        style_dict.update({
            "document_link_start": Markup("<a href='https://www.viindoo.com/documentation' target='_blank'>"),
            "slides_link_start": Markup("<a href='https://www.viindoo.com/slides' target='_blank'>"),
        })
        return style_dict

    def _get_answer(self, channel, body, message, command=False):
        answer = super()._get_answer(channel, body, message, command)
        if not answer:
            return answer
        if isinstance(answer, list):
            return [self._rebrand_answer(item) for item in answer]
        return self._rebrand_answer(answer)

    @staticmethod
    def _rebrand_answer(answer):
        """Name the product of the bot in its own language: the answers of core are translated, so the
        brand is replaced in the text that is sent."""
        return answer.replace('OdooBot', 'ViindooBot').replace('Odoo', 'Viindoo')
