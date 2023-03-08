from odoo import models

class Channel(models.Model):
    _inherit = 'slide.channel'   

    def _default_cover_properties(self):
        """ Cover properties defaults are overridden to keep a consistent look for the slides
        channels headers across Odoo versions (pre-customization, with purple gradient fitting the
        homepage images, etc). Furthermore, as adding padding to the cover would not look great,
        its height is set to fit to content (snippet option to change this also disabled on the view).""" 
        res = super(Channel,self)._default_cover_properties()
        res['background_color_style'] = (
                'background-color: rgba(0, 0, 0, 0); '
                'background-image: linear-gradient(90deg, #00bbce, #7f4282);'
            )
        return res
