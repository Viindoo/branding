from odoo import models


class Channel(models.Model):
    _inherit = 'slide.channel'

    def _default_cover_properties(self):
        """Give the header of a new course the Viindoo gradient, teal to purple."""
        res = super()._default_cover_properties()
        # The brand colours as literals: the SCSS tokens are not readable from Python.
        res['background_color_style'] = (
            'background-color: rgba(0, 0, 0, 0); '
            'background-image: linear-gradient(90deg, #00bbce, #7f4282);'
        )
        return res
