from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestViinBrandInstallAssets(HttpCase):
    """The passive branding binaries of viin_brand (favicon, logo, app-tile PNGs) are reachable over HTTP."""

    def test_branding_static_assets_serve(self):
        """The branding static assets (favicon, Viindoo logo, one app tile) are served over HTTP 200."""
        for asset_url in (
            '/viin_brand/static/img/favicon.ico',
            '/viin_brand/static/img/Viindoo-logo.svg',
            '/viin_brand/static/img/apps/crm.png',
        ):
            res = self.url_open(asset_url)
            self.assertEqual(
                res.status_code, 200,
                "Branding asset %s must be served with HTTP 200" % asset_url,
            )
