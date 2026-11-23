import json

from odoo import http
from odoo.http import request
from odoo.tools import file_open
from odoo.tools.binary import BinaryBytes

from odoo.addons.web.controllers.webmanifest import WebManifest

# The Viindoo chrome colour, the browser theme colour of the web manifest and of the theme-color meta
# (views/webclient_templates.xml); it equals the SCSS `$o-viin-chrome-base` in
# static/src/scss/brand_variables.scss.
VIINDOO_THEME_COLOR = '#007F8E'

# The Viindoo brand colour that paints content (default colours of the emails and of the livechat
# channels); it equals the SCSS `$o-brand-primary` in static/src/scss/brand_variables.scss.
VIINDOO_BRAND_COLOR = '#7F4282'

# Default of the ``web.web_app_name`` ir.config_parameter; only this stock value is de-branded.
CORE_DEFAULT_APP_NAME = 'Odoo'

MANIFEST_CONTENT_TYPE = 'application/manifest+json'


class BrandWebManifest(WebManifest):

    def _get_webmanifest(self):
        """Re-brand the backend PWA manifest: name, colours and icons.

        The name is replaced only while it still holds the stock default, so a PWA name the
        customer configured is kept.
        """
        manifest = super()._get_webmanifest()
        if manifest.get('name') == CORE_DEFAULT_APP_NAME:
            manifest['name'] = self._viindoo_app_name()
        manifest['theme_color'] = VIINDOO_THEME_COLOR
        manifest['background_color'] = VIINDOO_THEME_COLOR
        icon_sizes = ['192x192', '512x512']
        manifest['icons'] = [{
            'src': '/' + self._viindoo_icon_path(size),
            'sizes': size,
            'type': 'image/png',
        } for size in icon_sizes]
        return manifest

    @http.route()
    def scoped_app_manifest(self, app_id, path, app_name=''):
        """Re-brand the colours of the scoped-app PWA manifest; name, scope and icons stay app-scoped.

        Core builds this manifest inline in the route, so the JSON body is re-serialised. Any
        response that is not a 200 manifest is returned untouched.
        """
        response = super().scoped_app_manifest(app_id, path, app_name=app_name)
        content_type = (response.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        if response.status_code != 200 or content_type != MANIFEST_CONTENT_TYPE:
            return response
        data = json.loads(response.get_data(as_text=True))
        data['theme_color'] = VIINDOO_THEME_COLOR
        data['background_color'] = VIINDOO_THEME_COLOR
        return request.make_json_response(data, {
            'Content-Type': MANIFEST_CONTENT_TYPE,
        })

    def _icon_path(self):
        """Return the Viindoo icon path in place of core's Odoo fallback icon.

        Core uses this path for the offline page and as the icon of every scoped app that has no
        ``icon.svg``. It is addons-relative without a leading slash, like core's.
        """
        return self._viindoo_icon_path()

    def _viindoo_app_name(self):
        return 'Viindoo'

    def _viindoo_icon_path(self, size='192x192'):
        return 'viin_brand/static/img/viindoo-icon-%s.png' % size

    @http.route()
    def offline(self):
        with file_open(self._viindoo_icon_path(), 'rb') as icon:
            return request.render('viin_brand.webclient_offline', {'viindoo_icon': BinaryBytes(icon.read())})
