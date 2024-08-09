from odoo.addons.web.tests.test_webmanifest import WebManifestRoutesTest
from odoo.tests.common import tagged


@tagged("-at_install", "post_install")
class BrandWebManifestRoutesTest(WebManifestRoutesTest):
    """
    Skip odoo test and replace similar test for viindoo
    """
    def test_brand_webmanifest(self):
        """
        This route returns a well formed backend's WebManifest
        """
        self.authenticate("admin", "admin")
        response = self.url_open("/web/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/manifest+json")
        data = response.json()
        self.assertEqual(data["name"], "Viindoo")
        self.assertEqual(data["scope"], "/web")
        self.assertEqual(data["start_url"], "/web")
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["background_color"], "#00bbce")
        self.assertEqual(data["theme_color"], "#00bbce")
        self.assertEqual(data["prefer_related_applications"], False)
        self.assertCountEqual(data["icons"], [
            {'src': '/viin_brand_common/static/img/viindoo-icon-192x192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': '/viin_brand_common/static/img/viindoo-icon-512x512.png', 'sizes': '512x512', 'type': 'image/png'}
        ])
        self.assertGreaterEqual(len(data["shortcuts"]), 0)
        for shortcut in data["shortcuts"]:
            self.assertGreater(len(shortcut["name"]), 0)
            self.assertGreater(len(shortcut["description"]), 0)
            self.assertGreater(len(shortcut["icons"]), 0)
            self.assertTrue(shortcut["url"].startswith("/web#menu_id="))

    def test_brand_webmanifest_unauthenticated(self):
        """
        This route returns a well formed backend's WebManifest
        """
        response = self.url_open("/web/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/manifest+json")
        data = response.json()
        self.assertEqual(data["name"], "Viindoo")
        self.assertEqual(data["scope"], "/web")
        self.assertEqual(data["start_url"], "/web")
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(data["background_color"], "#00bbce")
        self.assertEqual(data["theme_color"], "#00bbce")
        self.assertEqual(data["prefer_related_applications"], False)
        self.assertCountEqual(data["icons"], [
            {'src': '/viin_brand_common/static/img/viindoo-icon-192x192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': '/viin_brand_common/static/img/viindoo-icon-512x512.png', 'sizes': '512x512', 'type': 'image/png'}
        ])
        self.assertEqual(len(data["shortcuts"]), 0)

    def test_brand_apple_touch_icon(self):
        """
        This request tests the presence of an apple-touch-icon image route for the PWA icon and
        its presence from the head of the document.
        """
        self.authenticate("demo", "demo")
        response = self.url_open("/viin_brand_common/static/img/viindoo-icon-ios.png")
        self.assertEqual(response.status_code, 200)

        document = self.url_open("/web")
        self.assertIn(
            '<link rel="apple-touch-icon" href="/viin_brand_common/static/img/viindoo-icon-ios.png"/>', document.text,
            "Icon for iOS is present in the head of the document.",
        )
