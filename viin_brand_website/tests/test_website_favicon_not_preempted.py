# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Locks the behavioral contract of the favicon-branding fix: Viindoo branding on
# `website.favicon` must be supplied as a DATA-level DEFAULT (models/website.py
# `_default_brand_favicon`), and must NEVER pre-empt a website's own configured favicon by
# rewriting the rendered `<link rel="shortcut icon">` at the QWeb level.
#
# The defect this replaces (see the header comment above the `layout` template in
# views/website_templates.xml) was an
#     <xpath expr="//t[@t-set='x_icon']" position="replace">
# inheriting `website.layout`. `locate_node` (odoo/tools/template_inheritance.py) resolves an
# xpath to the FIRST document-order match in the combined arch, which is core website's own
# producer (the `website.layout` template in website/views/website_templates.xml -
# `<t t-set="x_icon" t-value="website.image_url(website, 'favicon')"/>`), so the replace destroyed
# it and hardcoded the brand path unconditionally, with no `or` guard - a customer who configured
# their own favicon could never serve it (AC-1 below). The fix moves branding to a field default
# instead, which only supplies a value when none exists yet, so a NEW website still starts branded
# (AC-2 below) without ever overriding a value the customer set.
#
# AC-1 grounding (Odoo 19.0 core; verified via odoo-semantic model_inspect against the checkout at
# /home/tran-ngoc-tuan/git/odoo_19.0/addons):
#   - the `website.layout` template in website/views/website_templates.xml sets
#     `x_icon = website.image_url(website, 'favicon')`.
#   - `Website.image_url(self, record, field, size=None)` in website/models/website.py (confirmed
#     present via odoo-semantic model_inspect at 19.0) returns
#       '/web/image/%s/%s/%s%s?unique=%s' % (record._name, record.id, field, size, sha)
#     i.e. for a website with no explicit size: /web/image/website/<id>/favicon?unique=<7 hex>
#     (sha = hashlib.sha512(str(record.write_date)...).hexdigest()[:7]).
#   - the `web.layout` template in web/views/webclient_templates.xml renders it:
#       <link type="image/x-icon" rel="shortcut icon" t-att-href="x_icon or '/web/static/img/favicon.ico'"/>
#
# The production fix (models/website.py) is ALREADY PRESENT in this tree, so the RED proof here is
# confirm-by-toggle, not red-before-green code absence:
#   - Restoring the deleted `//t[@t-set='x_icon']` replace xpath into views/website_templates.xml's
#     `layout` template must turn WebsiteFaviconNotPreemptedTest red (the rendered href collapses to
#     the hardcoded brand path regardless of the website's own configured favicon).
#   - Reverting the `favicon` field default in models/website.py to core's own `_default_favicon`
#     must turn BrandedFaviconDefaultTest red (a new website would start with core's own icon).
import base64
import re

from PIL import Image

from odoo import tools
from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools.image import image_to_base64

# Fixture path for the branded asset - mirrors models/website.py's own BRAND_FAVICON_PATH, kept as
# an independent literal (not imported from the code under test) so this asserts against the
# actual asset on disk, not a value borrowed from production.
BRAND_FAVICON_PATH = "viin_brand/static/img/favicon.ico"

# The hardcoded href the removed QWeb override used to force onto every website, unconditionally.
# A regression that re-introduces the override makes the homepage's shortcut-icon href equal this
# again, no matter what the website's own `favicon` field holds.
BRAND_FAVICON_HREF = "/viin_brand/static/img/favicon.ico"

# Parses the shortcut-icon <link> href out of server-rendered HTML - mirrors
# viin_brand_common/tests/test_debrand_layout.py's convention for the same job.
_LINK_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
_SHORTCUT_ICON_RE = re.compile(r'rel\s*=\s*["\']shortcut icon["\']', re.IGNORECASE)
_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


@tagged("post_install", "-at_install")
class BrandedFaviconDefaultTest(TransactionCase):
    """AC-2: a newly created website must start branded, not with core's own default favicon."""

    def test_new_website_defaults_to_the_viindoo_favicon(self):
        """A website created with no explicit `favicon` must default to the Viindoo asset.

        Business rule: a fresh Viindoo deployment starts branded out of the box. Asserts on the
        resulting field VALUE - not on `_default_brand_favicon` having been called - so a refactor
        that keeps the same outcome through a different mechanism still passes."""
        Website = self.env["website"]
        with tools.file_open(BRAND_FAVICON_PATH, "rb") as f:
            expected_brand_favicon = base64.b64encode(f.read())
        # Core's own default (website/models/website.py `_default_favicon`), used here purely as
        # the "unbranded" reference value - it is not overridden by this module, only bypassed via
        # a `super()` fallback when the brand asset is missing (not this case).
        core_default_favicon = Website._default_favicon()

        website = Website.create({"name": "AC-2 Branded Website"})

        self.assertEqual(
            website.favicon, expected_brand_favicon,
            "a newly created website's favicon must be the Viindoo asset at %s byte-for-byte; it "
            "is not, so the DATA-level default is missing, reverted, or reading the wrong asset"
            % BRAND_FAVICON_PATH,
        )
        self.assertNotEqual(
            website.favicon, core_default_favicon,
            "a newly created website's favicon must not be core's own default "
            "(web/static/img/favicon.ico) - a Viindoo deployment must start branded",
        )


@tagged("post_install", "-at_install")
class WebsiteFaviconNotPreemptedTest(HttpCase):
    """AC-1: a website's own configured favicon must survive rendering, never pre-empted by brand."""

    def _favicon_href(self, html):
        """Return the href of the rendered shortcut-icon <link>, or None when absent."""
        for link in _LINK_RE.findall(html):
            if _SHORTCUT_ICON_RE.search(link):
                href = _HREF_RE.search(link)
                return href.group(1) if href else None
        return None

    def test_configured_website_favicon_is_not_preempted_by_brand_default(self):
        """A website with its OWN favicon configured must serve that favicon, not the brand asset.

        Business rule: branding is a default, never an override - the moment a customer sets their
        own favicon, it must render. Fetches a real frontend page (the homepage) and reads the
        actual shortcut-icon href core renders, rather than asserting on any internal call."""
        website = self.env.ref("website.default_website")
        distinctive_favicon = image_to_base64(Image.new("RGB", (16, 16), color=(1, 2, 3)), "PNG")
        website.write({"favicon": distinctive_favicon})

        response = self.url_open("/")
        self.assertEqual(response.status_code, 200, "the website homepage must render")

        href = self._favicon_href(response.text)
        self.assertIsNotNone(
            href, "the homepage must render a shortcut-icon <link> with an href"
        )

        # website.image_url()'s href shape for THIS website's own `favicon` field
        # (`Website.image_url` in website/models/website.py), parametrized on this record's own id
        # so a favicon served for a different website could not accidentally pass.
        own_favicon_href_re = re.compile(
            r"^/web/image/website/%d/favicon\?unique=[0-9a-f]{7}$" % website.id
        )
        self.assertRegex(
            href, own_favicon_href_re,
            "the rendered shortcut-icon href must point at website %d's OWN favicon via core's "
            "website.image_url() (/web/image/website/%d/favicon?unique=<sha>); got %r instead - a "
            "QWeb override pre-empting x_icon would produce exactly this failure"
            % (website.id, website.id, href),
        )
        self.assertNotEqual(
            href, BRAND_FAVICON_HREF,
            "the homepage favicon must not be pre-empted by the hardcoded brand path %s - that is "
            "exactly what the removed `//t[@t-set='x_icon']` QWeb override used to force regardless "
            "of the website's own configured favicon" % BRAND_FAVICON_HREF,
        )


@tagged("post_install", "-at_install")
class UntouchedFaviconsGetBrandedTest(TransactionCase):
    """AC-3: websites a field default could never reach must still end up branded - but ONLY those.

    A `default=` fires at record CREATION, so it never reaches `website.default_website` (core
    creates it while loading the `website` module, before this module's field extension exists) nor
    any website predating this module's install. While the QWeb `x_icon` override was in place those
    records still LOOKED branded, because the override forced the brand path at render time for
    every website regardless of the stored field. Removing that override - correct, since it
    destroyed website's own producer - makes the stored value render, so those records would fall
    back to Odoo's icon. `__init__._brand_untouched_favicons` corrects them once, and both entry
    points (the `post_init_hook` and migrations/0.1.2) delegate to it, so exercising it here covers
    the install and upgrade paths alike.

    The two assertions below are deliberately opposed: doing nothing fails the first, and
    overwriting indiscriminately fails the second.
    """

    def test_only_websites_still_holding_cores_default_favicon_get_branded(self):
        from .. import _brand_untouched_favicons

        Website = self.env["website"]
        core_default_favicon = Website._default_favicon()

        # One website left exactly as core would have created it - the population a field default
        # cannot reach.
        untouched = Website.create({"name": "AC-3 Untouched"})
        untouched.write({"favicon": core_default_favicon})
        self.assertEqual(
            untouched.favicon, core_default_favicon,
            "fixture precondition: this website must start out holding core's own default favicon",
        )

        # One website whose owner deliberately configured a favicon. write() normalises through
        # website._handle_favicon, so read the STORED value back and treat that as the baseline -
        # comparing against the pre-write literal would test Odoo's image pipeline, not this fix.
        configured = Website.create({"name": "AC-3 Configured"})
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
            "a website still holding core's stock favicon must be branded - it is one of the "
            "records a field default can never reach, and since the QWeb x_icon override was "
            "removed nothing else supplies branding for it",
        )
        self.assertTrue(
            untouched.favicon,
            "the branded favicon must be a real value, never emptied",
        )
        self.assertEqual(
            configured.favicon, configured_baseline,
            "a website whose owner configured its favicon must be left byte-identical - rewriting "
            "it is precisely the regression that removing the QWeb override was meant to fix",
        )
