# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The Viindoo favicon is the default of `website.favicon` (models/website.py), never a QWeb
# override of the rendered `<link rel="shortcut icon">`: an override on `x_icon` would hide a
# favicon the customer configured.
import io
import re

from PIL import Image

from odoo import tools
from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools import BinaryBytes


def _png_favicon(color):
    """A one-colour PNG favicon, as the binary value a website stores."""
    output = io.BytesIO()
    Image.new("RGB", (16, 16), color=color).save(output, "PNG")
    return BinaryBytes(output.getvalue())


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
            expected_brand_favicon = f.read()
        core_default_favicon = bytes(Website._default_favicon())

        website = Website.create({"name": "Branded Website"})

        self.assertEqual(
            bytes(website.favicon), expected_brand_favicon,
            "a newly created website's favicon must be the Viindoo asset at %s byte-for-byte"
            % BRAND_FAVICON_PATH,
        )
        self.assertNotEqual(
            bytes(website.favicon), core_default_favicon,
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
        website = self.env.ref("base.default_website")
        website.write({"favicon": _png_favicon((1, 2, 3))})

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

    A default applies when a record is created, so it misses ``base.default_website``, which is
    created while ``website`` loads. `__init__._brand_untouched_favicons` brands the websites that
    still hold core's favicon when the module is installed.
    """

    def test_only_websites_still_holding_cores_default_favicon_get_branded(self):
        from .. import _brand_untouched_favicons

        Website = self.env["website"]
        core_default_favicon = bytes(Website._default_favicon())
        with tools.file_open(BRAND_FAVICON_PATH, "rb") as f:
            brand_favicon = f.read()

        untouched = Website.create({"name": "Untouched"})
        untouched.write({"favicon": BinaryBytes(core_default_favicon)})
        self.assertEqual(
            bytes(untouched.favicon), core_default_favicon,
            "fixture precondition: this website must start out holding core's own default favicon",
        )

        configured = Website.create({"name": "Configured"})
        configured.write({"favicon": _png_favicon((9, 8, 7))})
        configured_baseline = bytes(configured.favicon)
        self.assertNotEqual(
            configured_baseline, core_default_favicon,
            "fixture precondition: the configured website must not coincidentally hold core's default",
        )

        _brand_untouched_favicons(self.env)

        self.assertEqual(
            bytes(untouched.favicon), brand_favicon,
            "a website still holding core's stock favicon must get the Viindoo favicon",
        )
        self.assertEqual(
            bytes(configured.favicon), configured_baseline,
            "a website whose owner configured its favicon must be left byte-identical",
        )

    def test_the_website_created_while_the_site_loads_is_branded_once_the_module_is_installed(self):
        with tools.file_open(BRAND_FAVICON_PATH, "rb") as f:
            brand_favicon = f.read()

        default_website = self.env.ref("base.default_website")

        self.assertEqual(bytes(default_website.favicon), brand_favicon)
