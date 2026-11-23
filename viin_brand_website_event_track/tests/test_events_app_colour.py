from lxml import html

from odoo.tests.common import HttpCase, tagged

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

# The colour core gives the events app: the Odoo purple.
CORE_EVENTS_COLOR = '#875A7B'


@tagged('post_install', '-at_install')
class TestEventsAppColour(HttpCase):

    def test_events_app_manifest_carries_the_viindoo_content_purple(self):
        """The manifest of the events app asks the browser for the Viindoo content purple and still
        describes the app of the website: its names are the ones core reads from the website, and
        its start address stays the one of its scope, as core builds them.

        WOULD FAIL IF REVERTED: without the controller override the manifest keeps the Odoo purple;
        an override that rebuilds the manifest instead of amending it drops core's keys."""
        website = self.env['website'].search([], limit=1)

        response = self.url_open('/event/manifest.webmanifest')

        self.assertEqual(response.status_code, 200)
        manifest = response.json()
        self.assertEqual(manifest['theme_color'].upper(), VIINDOO_BRAND_COLOR.upper())
        self.assertNotEqual(manifest['theme_color'].upper(), CORE_EVENTS_COLOR.upper())
        self.assertEqual(manifest['name'], website.events_app_name)
        self.assertEqual(manifest['short_name'], website.events_app_name)
        self.assertEqual(manifest['start_url'], manifest['scope'])

    def test_event_pages_ask_the_browser_for_the_viindoo_content_purple(self):
        """The head of the event pages carries one theme-color meta, the Viindoo content purple.

        WOULD FAIL IF REVERTED: without the template inheritance the page keeps the Odoo purple."""
        response = self.url_open('/event')

        self.assertEqual(response.status_code, 200)
        colours = html.fromstring(response.content).xpath("//meta[@name='theme-color']/@content")
        self.assertEqual([colour.upper() for colour in colours], [VIINDOO_BRAND_COLOR.upper()])
