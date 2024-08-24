import json
import logging
import base64

from odoo import http
from odoo.http import request
from odoo.tools import ustr, file_open

from odoo.addons.web.controllers.webmanifest import WebManifest

_logger = logging.getLogger(__name__)


class BrandWebManifest(WebManifest):

    @http.route()
    def webmanifest(self):
        response = super(BrandWebManifest, self).webmanifest()
        json_data = response.get_data(as_text=True)

        json_response = json.loads(json_data)

        json_response['theme_color'] = '#00bbce'
        json_response['background_color'] = '#00bbce'
        json_response['name'] = 'Viindoo'

        icon_sizes = ['192x192', '512x512']
        invalid_sizes = [item['sizes'] for item in json_response.get('icons', []) if item['sizes'] not in icon_sizes]
        if invalid_sizes:
            _logger.warning("odoo's list icon has changed")

        json_response['icons'] = [{
            'src': '/' + self._viindoo_icon_path(size),
            'sizes': size,
            'type': 'image/png',
        } for size in icon_sizes]

        new_json_data = json.dumps(json_response, default=ustr)

        new_response = request.make_response(new_json_data, [
            ('Content-Type', 'application/manifest+json'),
        ])

        return new_response

    def _viindoo_icon_path(self, size='192x192'):
        return 'viin_brand_common/static/img/viindoo-icon-%s.png' % size

    @http.route()
    def offline(self):
        """ Returns the offline page delivered by the service worker """
        return request.render('viin_brand_common.webclient_offline', {
            'viindoo_icon': base64.b64encode(file_open(self._viindoo_icon_path(), 'rb').read())
        })
