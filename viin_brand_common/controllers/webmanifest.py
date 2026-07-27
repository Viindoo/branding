import base64
import json

from odoo import http
from odoo.http import request
from odoo.tools import file_open

from odoo.addons.web.controllers.webmanifest import WebManifest

# Single Python brand-hex SSOT (DESIGN 2.2/2.3/5, ODOO-AI-ETHOS #11). The Viindoo brand colour is
# declared here ONCE on the Python side; it must equal the SCSS $o-brand-primary in
# static/src/scss/brand_variables.scss (asserted equal by tests/test_brand_ssot.py).
VIINDOO_THEME_COLOR = '#00BBCE'

# The UNTOUCHED core default of the ``web.web_app_name`` ir.config_parameter - core 19.0
# web/controllers/webmanifest.py `_get_webmanifest` reads
# ``get_param('web.web_app_name', 'Odoo')``. De-branding replaces ONLY this stock value; see
# `_get_webmanifest` below.
CORE_DEFAULT_APP_NAME = 'Odoo'

# The content type core serves both PWA manifests with (`webmanifest` and `scoped_app_manifest`
# both pass it to ``request.make_json_response``). Used to decide whether a ``super()`` response is
# really a manifest body this controller may safely re-serialise.
MANIFEST_CONTENT_TYPE = 'application/manifest+json'


class BrandWebManifest(WebManifest):

    def _get_webmanifest(self):
        """De-brand the backend PWA manifest to Viindoo, sourcing the colours from the single
        brand-hex SSOT. Overriding the builder (not the ``webmanifest`` route) keeps the core
        route, headers and shortcut/scope metadata and only re-brands name, colours and icons."""
        manifest = super()._get_webmanifest()
        # De-brand the PWA app NAME only when it still holds the untouched Odoo default. Core
        # resolves it from the ``web.web_app_name`` ir.config_parameter, so overwriting it
        # unconditionally silently discarded a customer's own PWA name on every manifest fetch -
        # a functional regression, not a de-brand. Same "substitute the stock default only"
        # contract this cluster already uses for the outgoing-notification colour
        # (viin_brand_mail/__init__.py `post_init_hook`, mail's stock '#875A7B'), and the same
        # read-super-then-fill-the-gap shape core itself uses in
        # addons/hr_expense/controllers/webmanifest.py.
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
        """De-brand the scoped-app PWA manifest from the SAME brand SSOT. Core 19.0 builds this
        manifest dict inline in the route (hardcoding #714B67) with no builder helper to override,
        so call super, then re-point theme/background colours to VIINDOO_THEME_COLOR; name, scope
        and icons stay app-scoped."""
        response = super().scoped_app_manifest(app_id, path, app_name=app_name)
        # Re-serialise ONLY an actual 200 manifest+json body. `super()` is not contractually a JSON
        # response: a future core - or another module ahead of us in the MRO - may legitimately
        # answer with a redirect or an error page, and `json.loads` on that body would raise and
        # turn this route into a 500. Anything that is not a manifest passes straight through
        # untouched (there is nothing to de-brand in it anyway).
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
        """De-brand the PWA FALLBACK icon core serves for apps that ship no ``icon.svg``.

        Core `_icon_path` returns ``web/static/img/odoo-icon-192x192.png`` and it is not only the
        offline-page icon: it is the fallback of `_get_scoped_app_icons` (every app without
        ``static/description/icon.svg``) and, through it, of the `scoped_app_icon_png` route that
        serves Safari's fixed-size PWA icon. Left un-overridden, the Install-App page of a
        de-branded database still shows the Odoo mascot.

        Returns the same addons-relative, leading-slash-less shape as core, because both core call
        sites build on that shape (``'/' + self._icon_path()`` and
        ``file_open(icon_src.removeprefix('/'))``).
        """
        return self._viindoo_icon_path()

    def _viindoo_app_name(self):
        return 'Viindoo'

    def _viindoo_icon_path(self, size='192x192'):
        return 'viin_brand_common/static/img/viindoo-icon-%s.png' % size

    @http.route()
    def offline(self):
        """ Returns the offline page delivered by the service worker """
        return request.render('viin_brand_common.webclient_offline', {
            'viindoo_icon': base64.b64encode(file_open(self._viindoo_icon_path(), 'rb').read())
        })
