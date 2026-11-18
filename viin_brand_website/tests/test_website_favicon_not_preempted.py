# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The Viindoo favicon is the default of `website.favicon` (models/website.py), never a QWeb
# override of the rendered `<link rel="shortcut icon">`: an override on `x_icon` would hide a
# favicon the customer configured.
import base64
import re

from PIL import Image

from odoo import tools
from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools.image import image_to_base64

BRAND_FAVICON_PATH = "viin_brand/static/img/favicon.ico"

# The href a QWeb override of `x_icon` would force onto every website.
BRAND_FAVICON_HREF = "/viin_brand/static/img/favicon.ico"


@tagged("post_install", "-at_install")
class BrandedFaviconDefaultTest(TransactionCase):
    """A newly created website starts branded, not with core's own default favicon."""

    def test_new_website_defaults_to_the_viindoo_favicon(self):
        """A website created with no explicit `favicon` defaults to the Viindoo asset."""
        Website = self.env["website"]
        with tools.file_open(BRAND_FAVICON_PATH, "rb") as f:
            expected_brand_favicon = base64.b64encode(f.read())
        core_default_favicon = Website._default_favicon()

        website = Website.create({"name": "Branded Website"})

        self.assertEqual(
            website.favicon, expected_brand_favicon,
            "a newly created website's favicon must be the Viindoo asset at %s byte-for-byte"
            % BRAND_FAVICON_PATH,
        )
        self.assertNotEqual(
            website.favicon, core_default_favicon,
            "a newly created website's favicon must not be core's own default "
            "(web/static/img/favicon.ico) - a Viindoo deployment must start branded",
        )


@tagged("post_install", "-at_install")
class WebsiteFaviconNotPreemptedTest(HttpCase):
    """A website's own configured favicon is rendered, never pre-empted by the brand asset."""

    def _favicon_href(self, html):
        """Return the href of the rendered shortcut-icon <link>, or None when absent."""
        for link in re.findall(r"<link\b[^>]*>", html, re.IGNORECASE):
            if re.search(r'rel\s*=\s*["\']shortcut icon["\']', link, re.IGNORECASE):
                href = re.search(r'href\s*=\s*["\']([^"\']+)["\']', link, re.IGNORECASE)
                return href.group(1) if href else None
        return None

    def test_configured_website_favicon_is_not_preempted_by_brand_default(self):
        """A website with its own favicon configured serves that favicon, not the brand asset.

        Branding is a default, never an override: reads the shortcut-icon href the homepage
        renders."""
        website = self.env.ref("website.default_website")
        distinctive_favicon = image_to_base64(Image.new("RGB", (16, 16), color=(1, 2, 3)), "PNG")
        website.write({"favicon": distinctive_favicon})

        response = self.url_open("/")
        self.assertEqual(response.status_code, 200, "the website homepage must render")

        href = self._favicon_href(response.text)
        self.assertIsNotNone(
            href, "the homepage must render a shortcut-icon <link> with an href"
        )

        own_favicon_href_re = re.compile(
            r"^/web/image/website/%d/favicon\?unique=[0-9a-f]{7}$" % website.id
        )
        self.assertRegex(
            href, own_favicon_href_re,
            "the rendered shortcut-icon href must point at website %d's own favicon "
            "(/web/image/website/%d/favicon?unique=<sha>); got %r" % (website.id, website.id, href),
        )
        self.assertNotEqual(
            href, BRAND_FAVICON_HREF,
            "the homepage favicon must not be pre-empted by the hardcoded brand path %s"
            % BRAND_FAVICON_HREF,
        )


@tagged("post_install", "-at_install")
class UntouchedFaviconsGetBrandedTest(TransactionCase):
    """Websites a field default never reaches are branded, and only those.

    A default applies when a record is created, so it misses ``website.default_website`` and the
    websites that predate the module. `__init__._brand_untouched_favicons` brands them for both
    the `post_init_hook` and the module migration, so exercising it covers both paths.
    """

    def test_only_websites_still_holding_cores_default_favicon_get_branded(self):
        from .. import _brand_untouched_favicons

        Website = self.env["website"]
        core_default_favicon = Website._default_favicon()

        untouched = Website.create({"name": "Untouched"})
        untouched.write({"favicon": core_default_favicon})
        self.assertEqual(
            untouched.favicon, core_default_favicon,
            "fixture precondition: this website must start out holding core's own default favicon",
        )

        # write() normalises the image, so the stored value is the baseline.
        configured = Website.create({"name": "Configured"})
        configured.write({
            "favicon": image_to_base64(Image.new("RGB", (16, 16), color=(9, 8, 7)), "PNG")
        })
        configured_baseline = configured.favicon
        self.assertNotEqual(
            configured_baseline, core_default_favicon,
            "fixture precondition: the configured website must not coincidentally hold core's default",
        )

        _brand_untouched_favicons(self.env)

        self.assertNotEqual(
            untouched.favicon, core_default_favicon,
            "a website still holding core's stock favicon must be branded",
        )
        self.assertTrue(
            untouched.favicon,
            "the branded favicon must be a real value, never emptied",
        )
        self.assertEqual(
            configured.favicon, configured_baseline,
            "a website whose owner configured its favicon must be left byte-identical",
        )
