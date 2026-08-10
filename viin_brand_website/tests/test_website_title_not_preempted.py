import base64

from lxml import html

from odoo import tools
from odoo.tests.common import HttpCase, tagged

# viin_brand_common's web.layout brand defaults (Viindoo/branding#654 fix,
# viin_brand_common/views/webclient_template.xml) are meant to be a
# last-resort FALLBACK for `title` / `x_icon`. On a `website`-rendered page,
# website.layout's own producers (per-page title, seo_object, favicon) must
# always win. Nothing in this repo asserted that until now - the currently
# open PR #661 (branding fork, head `acc5474`) proved the opposite is easy
# to break: its `//head position="before"` anchor lands the brand t-set
# nodes OUTSIDE <head> and BEFORE website.layout's `<t t-if="not title">`
# guard (website/views/website_templates.xml), so every website page
# silently collapsed to <title>Viindoo</title> with zero OpenGraph/Twitter
# meta. This module - the only branding module that legitimately depends on
# `website` - owns that cross-module contract.
BRAND_TITLE = "Viindoo"
BRAND_FAVICON = "/viin_brand/static/img/favicon.ico"
WEBSITE_NAME = "Test Website"


@tagged("-at_install", "post_install")
class TestWebsiteTitleNotPreempted(HttpCase):
    """The brand default title/favicon fallback must never pre-empt a value
    a website-rendered page produces itself.

    All three tests hit the SAME route (`/contactus` - a `website.page`
    shipped by base `website`, no `website_crm` dependency needed,
    `website/data/website_data.xml:524-547`) so they exercise exactly the
    producer chain PR #661 broke: website.layout's `<t t-if="not title">`
    guard (title + seo_object), its OpenGraph/Twitter meta block, and its
    unconditional favicon `t-set`.
    """

    def setUp(self):
        super().setUp()
        # Precondition guard (load-bearing): viin_brand_website deliberately
        # does NOT depend on viin_brand_common (see __manifest__.py
        # 'depends': ['website']) - adding that edge for one test would
        # change the module graph for zero behavioural gain. The edge is
        # expected to always be satisfied in practice because
        # viin_brand_common declares `auto_install: ['web']` and every
        # database with `website` installed also has `web` installed
        # (`website` depends on `web`). Assert that assumption explicitly
        # instead of silently relying on it.
        brand_common = self.env["ir.module.module"].sudo().search([
            ("name", "=", "viin_brand_common"),
            ("state", "=", "installed"),
        ], limit=1)
        if not brand_common:
            self.skipTest(
                "viin_brand_common is not installed on this database - this "
                "test protects the contract between its web.layout brand "
                "default and website.layout's own producers, so it is "
                "meaningless without it. viin_brand_website does not "
                "depend on viin_brand_common directly; it is expected to "
                "arrive via viin_brand_common's own auto_install: ['web'] "
                "since website depends on web. If this fires, that "
                "assumption no longer holds and needs investigation."
            )

        self.website = self.env.ref("website.default_website")
        self.website.write({"name": WEBSITE_NAME})

    def test_website_page_title_is_not_preempted_by_brand_default(self):
        """AC-W1: a website page's own title must win over the brand
        default - it must never render as the literal brand fallback.

        Falsifiable against PR #661: under its `//head position="before"`
        anchor, `title` is already bound to the brand default before
        website.layout's `<t t-if="not title">` producer runs, so that
        producer's `not title` is False and it never sets a per-page title.
        The page renders `<title>Viindoo</title>` instead of the website's
        own title. This assertion fails loudly under that anchor and passes
        under the chosen fix (`//head/meta[last()] position="after"`,
        strictly downstream of website.layout's producer).
        """
        response = self.url_open("/contactus")
        self.assertEqual(response.status_code, 200)

        document = html.fromstring(response.content)
        titles = document.xpath("//title")
        self.assertEqual(
            len(titles), 1,
            "exactly one <title> must render on a website page",
        )
        title_text = titles[0].text_content()
        self.assertNotEqual(
            title_text, BRAND_TITLE,
            "the brand default must not pre-empt website.layout's own "
            "title producer on a website-rendered page",
        )
        self.assertTrue(
            title_text.endswith(WEBSITE_NAME),
            "the page title must end with the configured website name "
            "(%r), got %r" % (WEBSITE_NAME, title_text),
        )

    def test_website_page_meta_survive_brand_default(self):
        """AC-W2: OpenGraph/Twitter meta must still be emitted - the
        assertion that would have caught PR #661's silent SEO loss.

        Falsifiable against PR #661: `seo_object` is assigned ONLY inside
        the same `<t t-if="not title">` guard as the per-page title
        (website/views/website_templates.xml). Under #661's anchor that
        guard is skipped (see the previous test's docstring), so
        `get_website_meta()` is never called and the page emits NOT ONE
        OpenGraph or Twitter meta tag - a silent, site-wide SEO and
        social-sharing regression nothing else in this repo tests. Both
        xpath queries below return empty lists under that anchor, which is
        exactly what fails this test.
        """
        response = self.url_open("/contactus")
        self.assertEqual(response.status_code, 200)

        document = html.fromstring(response.content)
        og_titles = document.xpath('//meta[@property="og:title"]')
        self.assertTrue(
            og_titles,
            'at least one <meta property="og:title"> must render - its '
            "absence means website.layout's seo_object producer was "
            "pre-empted (the Viindoo/branding#661 regression)",
        )
        self.assertTrue(
            any(meta.get("content") for meta in og_titles),
            "the og:title meta must carry real content, not an empty "
            "placeholder",
        )

        twitter_cards = document.xpath('//meta[@name="twitter:card"]')
        self.assertTrue(
            twitter_cards,
            'at least one <meta name="twitter:card"> must render - its '
            "absence means the whole Twitter card block was skipped",
        )

    def test_website_favicon_wins_over_brand_default(self):
        """AC-W3: the website's OWN configured favicon must win on a
        website page - a product-decision LOCK (design doc D5), NOT a
        #661-regression-detection assertion.

        website.layout sets `x_icon` UNCONDITIONALLY
        (`t-set="x_icon" t-value="website.image_url(website, 'favicon')"`)
        at `//head/*[1] position="before"` - strictly upstream of every
        anchor candidate this fix ever considered (the fatal base `//title`
        anchor, PR #661's `//head position="before"`, and the chosen
        `//head/meta[last()] position="after"`). The website's own favicon
        already wins under all three, so this assertion does NOT
        discriminate the #661 regression - it locks the separate, already
        settled product ruling that a website's genuine per-website favicon
        setting must never be overridden by the brand default. A future
        "fix" that forced the brand favicon over this setting would flip
        this assertion - exactly what it exists to prevent.
        """
        response = self.url_open("/contactus")
        self.assertEqual(response.status_code, 200)

        document = html.fromstring(response.content)
        favicons = document.xpath('//link[@rel="shortcut icon"]')
        self.assertTrue(favicons, "a shortcut icon <link> must render")
        href = favicons[0].get("href") or ""
        self.assertTrue(
            href.startswith("/web/image/website/"),
            "the website's own configured favicon must be served, got %r" % href,
        )
        self.assertNotEqual(
            href, BRAND_FAVICON,
            "the brand default favicon must not override the website's "
            "own configured favicon on a website-rendered page",
        )


@tagged("-at_install", "post_install")
class TestWebsiteFaviconDefault(HttpCase):
    """The brand favicon must be a DEFAULT, not an override.

    Two properties have to hold at once, and the pair is the whole point:
    a fresh website starts branded, AND a website that sets its own favicon
    actually gets to serve it. The QWeb `position="replace"` this module used to
    carry gave the first and destroyed the second.
    """

    def test_new_website_starts_with_the_brand_favicon(self):
        website = self.env["website"].create({"name": "Fresh Site"})
        with tools.file_open("viin_brand/static/img/favicon.ico", "rb") as f:
            expected = base64.b64encode(f.read())
        self.assertEqual(
            website.favicon,
            expected,
            "a newly created website must start with the brand favicon, not Odoo's",
        )

    def test_a_configured_favicon_is_not_overwritten_by_the_default(self):
        website = self.env["website"].create({"name": "Custom Site"})
        branded = website.favicon
        # A 1x1 PNG - content is irrelevant, only that it is the customer's own.
        custom = base64.b64encode(
            base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
            )
        )
        website.favicon = custom
        self.assertNotEqual(
            website.favicon,
            branded,
            "a favicon the customer set must survive - the brand value is a default, "
            "not an override",
        )
