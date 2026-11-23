import re
from urllib.parse import urlsplit

from odoo.addons.viin_brand.tools import VIINDOO_SOCIAL_LINKS
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

JS_MODULE = 'viin_brand/static/src/core/social_links/viindoo_social_links.js'
# The hosts a network is served from.
NETWORK_HOSTS = {
    'social_facebook': {'facebook.com'},
    'social_linkedin': {'linkedin.com'},
    'social_twitter': {'twitter.com', 'x.com'},
    'social_youtube': {'youtube.com'},
    'social_instagram': {'instagram.com'},
    'social_github': {'github.com'},
    'social_tiktok': {'tiktok.com'},
}
# A YouTube channel is named by an opaque identifier, which cannot carry the brand name.
YOUTUBE_CHANNEL_PATH = re.compile(r'^/channel/UC[\w-]{22}$')


@tagged('post_install', '-at_install')
class TestViindooSocialLinks(TransactionCase):
    """The Viindoo social accounts are declared once for Python and once for JS, and are Viindoo's."""

    def _js_links(self):
        with file_open(JS_MODULE) as js_file:
            source = js_file.read()
        table = re.search(r'VIINDOO_SOCIAL_LINKS\s*=\s*\{(.*?)\}', source, re.DOTALL)
        self.assertTrue(table, 'the JS module declares no VIINDOO_SOCIAL_LINKS table')
        return dict(re.findall(r'(\w+)\s*:\s*"([^"]+)"', table.group(1)))

    def test_python_and_js_declare_the_same_accounts(self):
        self.assertEqual(self._js_links(), VIINDOO_SOCIAL_LINKS)

    def test_every_network_has_a_viindoo_account(self):
        self.assertEqual(set(VIINDOO_SOCIAL_LINKS), set(NETWORK_HOSTS))
        for network, url in VIINDOO_SOCIAL_LINKS.items():
            with self.subTest(network=network):
                parts = urlsplit(url)
                self.assertEqual(parts.scheme, 'https')
                self.assertIn(parts.hostname.removeprefix('www.'), NETWORK_HOSTS[network])
                self.assertNotIn('odoo', url.lower())
                if network == 'social_youtube':
                    self.assertRegex(parts.path, YOUTUBE_CHANNEL_PATH)
                else:
                    self.assertIn('viindoo', url.lower())

    def test_the_bundles_serve_the_accounts(self):
        for bundle_name in ('web.assets_backend', 'web.assets_frontend'):
            bundle = self.env['ir.qweb']._get_asset_bundle(bundle_name, css=False, js=True, debug_assets=True)
            js = (bundle.js().raw or b'').decode('utf-8', 'replace')
            for network, url in VIINDOO_SOCIAL_LINKS.items():
                with self.subTest(bundle=bundle_name, network=network):
                    self.assertIn('"%s"' % url, js)
