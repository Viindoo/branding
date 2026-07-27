from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestViinBrandInstallAssets(HttpCase):
    """viin_brand must install clean on Odoo 19.0 and its brand static assets must serve.

    Baseline install-safety gate for the v16 -> v19 upgrade: the module ships
    ``installable: False`` and only reaches green once the module is actually
    installable and installs without error on 19.0, at which point its passive
    branding binaries (favicon, logo, app-tile PNGs) are reachable over HTTP.
    """

    def test_module_installs_clean_on_19(self):
        """viin_brand is present and fully installed on the 19.0 database."""
        module = self.env['ir.module.module'].search([('name', '=', 'viin_brand')])
        self.assertTrue(module, "viin_brand module record must exist in the registry")
        self.assertEqual(
            module.state, 'installed',
            "viin_brand must install clean on 19.0 (installable flag flipped, no install error)",
        )

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
