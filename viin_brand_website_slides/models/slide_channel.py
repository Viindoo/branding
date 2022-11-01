# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import io
import logging
import re
import requests
import PyPDF2

from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug, url_for
from odoo.exceptions import RedirectWarning, UserError, AccessError
from odoo.http import request
from odoo.tools import html2plaintext, sql

_logger = logging.getLogger(__name__)


class Channel(models.Model):
    _inherit = 'slide.channel'   
    
    def _default_cover_properties(self):
        """ Cover properties defaults are overridden to keep a consistent look for the slides
        channels headers across Odoo versions (pre-customization, with purple gradient fitting the
        homepage images, etc). Furthermore, as adding padding to the cover would not look great,
        its height is set to fit to content (snippet option to change this also disabled on the view)."""
        res = super()._default_cover_properties()
        res['background_color_style'] = (
                'background-color: rgba(0, 0, 0, 0); '
                'background-image: linear-gradient(90deg, #00bbce, #7f4282);'
            ),
        return res
   