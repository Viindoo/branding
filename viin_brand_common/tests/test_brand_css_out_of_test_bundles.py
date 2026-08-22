import logging
import re

from odoo.tests.common import HttpCase, tagged

_logger = logging.getLogger(__name__)

MODULE = "viin_brand_common"

# The two bundles core's own JS unit tests are served from. Both pull in
# web.assets_backend with ('include', ...) (addons/web/__manifest__.py), which
# is how this module's SCSS used to reach them in the first place.
CORE_TEST_BUNDLES = ("web.assets_unit_tests_setup", "web.tests_assets")

# The bundle the real webclient is served from - the counterweight side of the
# same contract.
WEBCLIENT_BUNDLE = "web.assets_web"

# The two stylesheets that carry the brand identity itself: the design tokens
# (colour, base font size) and the Bootstrap overrides (square corners). Named
# individually because these are the files whose values the brand appearance
# tours assert; if one of them ever stops reaching the real webclient, the
# product silently loses its identity while every bundle still compiles.
BRAND_IDENTITY_STYLESHEETS = (
    "/%s/static/src/scss/primary_variables.scss" % MODULE,
    "/%s/static/src/scss/bootstrap_overridden.scss" % MODULE,
)

# Odoo's SCSS compiler prefixes every source file it concatenates with a
# comment naming that file's path. Matching on the FULL comment - "/* " then a
# leading slash then the module name - and never on the bare module name is
# load-bearing: a bare substring search for "web_responsive" also matches
# "viin_customizer_web_responsive", and a bare search for a module name would
# equally match any module that merely has it as a suffix. That mistake
# produces a red run with nothing wrong, which is worse than no test.
MODULE_MARKER_RE = re.compile(r"/\* (/%s/[^*]*) \*/" % re.escape(MODULE))

# The theme colour core's own unit tests assert (html_editor's
# color_selector.test.js expects rgb(113, 75, 103) = #714B67). Sourced from
# core's contract, not from anything in this repository.
CORE_THEME_COLOUR_RE = re.compile(r"--o-color-1:\s*#714B67", re.IGNORECASE)


@tagged("-at_install", "post_install")
class TestBrandCssOutOfCoreTestBundles(HttpCase):
    """Brand CSS must reach the real webclient and NOTHING ELSE.

    The whole point of the ``('remove', ...)`` directives in this module's
    manifest is a separation that runs in exactly two directions, so both are
    asserted here:

    * core's JS unit-test page must compile with core's own design tokens, so
      core's tests measure core rather than Viindoo;
    * the real webclient must still receive every one of those stylesheets, so
      the user's product is untouched.

    A test that only checked the first direction would go green if somebody
    "fixed" a red run by deleting the brand stylesheets outright.

    These assertions read the CSS a browser is actually served, over HTTP, at
    the bundle's real hashed URL - which is also what makes them immune to the
    stale-bundle trap that cost this campaign a whole measurement round: when
    an SCSS edit breaks compilation, Odoo keeps serving the PREVIOUS bundle and
    an inspection of the source files alone reports success.
    """

    def _fetch_bundle_css(self, bundle_name):
        """Return ``(url, css)`` for ``bundle_name`` as actually served."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachment = bundle.css()
        self.assertTrue(
            attachment,
            "%s produced no CSS at all - the bundle failed to compile, and "
            "every other assertion about its contents would be meaningless"
            % bundle_name,
        )
        url = attachment[0].url
        response = self.url_open(url)
        self.assertEqual(
            response.status_code,
            200,
            "the compiled CSS of %s must be served at %s" % (bundle_name, url),
        )
        # Decode explicitly: requests guesses latin-1 for a text/* response that
        # carries no charset, which silently mangles any non-ASCII content.
        css = response.content.decode("utf-8")
        _logger.info(
            "[brand-css-guard] %s served from %s (%d bytes)",
            bundle_name,
            url,
            len(response.content),
        )
        return url, css

    def test_brand_stylesheets_are_absent_from_core_unit_test_bundles(self):
        """No stylesheet of this module may reach core's unit-test pages.

        Asserted as "none of this module's files", not as one named file: the
        contract is that the whole cluster stays out. Listing files instead
        would keep passing the day somebody adds a new brand stylesheet to
        web.assets_backend and forgets the matching removal - which is the
        exact regression this test exists to catch.
        """
        for bundle_name in CORE_TEST_BUNDLES:
            with self.subTest(bundle=bundle_name):
                url, css = self._fetch_bundle_css(bundle_name)
                leaked = sorted(set(MODULE_MARKER_RE.findall(css)))
                self.assertFalse(
                    leaked,
                    "%s (served at %s) still compiles %d stylesheet(s) of %s "
                    "into core's unit-test page: %s. Core's own tests then "
                    "measure Viindoo's design tokens instead of core's, which "
                    "is what made 8 core tests red before this fix."
                    % (bundle_name, url, len(leaked), MODULE, ", ".join(leaked)),
                )

    def test_core_unit_test_bundles_compile_cores_own_theme_colour(self):
        """The unit-test page must resolve o-color-1 to core's own #714B67.

        The absence check above proves this module's files are not concatenated
        into the bundle. This one proves the bundle that WAS produced actually
        carries core's value - a different witness of the same separation, and
        the one that fires if the removal ever happens by a route that leaves
        the brand value baked in anyway.
        """
        for bundle_name in CORE_TEST_BUNDLES:
            with self.subTest(bundle=bundle_name):
                url, css = self._fetch_bundle_css(bundle_name)
                self.assertTrue(
                    CORE_THEME_COLOUR_RE.search(css),
                    "%s (served at %s) does not resolve --o-color-1 to core's "
                    "own #714B67. core's html_editor colour tests assert "
                    "rgb(113, 75, 103) against this exact value."
                    % (bundle_name, url),
                )

    def test_brand_stylesheets_are_still_served_to_the_real_webclient(self):
        """Removing brand CSS from the TEST page must not touch the product.

        This is the assertion that stops the separation being "achieved" by
        dropping the branding altogether: it fails the moment a removal
        directive is aimed at the webclient bundle rather than the test ones.
        """
        url, css = self._fetch_bundle_css(WEBCLIENT_BUNDLE)
        for stylesheet in BRAND_IDENTITY_STYLESHEETS:
            with self.subTest(stylesheet=stylesheet):
                self.assertIn(
                    "/* %s */" % stylesheet,
                    css,
                    "%s (served at %s) no longer compiles %s. The real "
                    "webclient must keep every brand stylesheet - only the "
                    "unit-test bundles lose them."
                    % (WEBCLIENT_BUNDLE, url, stylesheet),
                )
