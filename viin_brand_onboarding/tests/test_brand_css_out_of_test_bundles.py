import re

from odoo.tests.common import HttpCase, tagged

from odoo.addons.viin_brand_common.tests.common import (
    BrandBundleCssMixin,
    CORE_TEST_BUNDLES,
    WEBCLIENT_BUNDLE,
    brand_marker_re,
)

MODULE = "viin_brand_onboarding"

# The one stylesheet this module owns. It is injected into web.assets_backend
# ('after', '/onboarding/static/src/scss/onboarding.scss', ...) and consumes
# five brand variables - $brand-primary-light/-dark/-darker and
# $brand-secondary-light/-dark - that only viin_brand_common's
# primary_variables.scss defines.
BRAND_STYLESHEET = "/%s/static/src/scss/onboarding.scss" % MODULE

# Every stylesheet marker owned by this module. See brand_marker_re() for why
# the anchoring on both sides of the module name is load-bearing - it matters
# more here than anywhere else in the brand cluster, because "viin_brand_
# onboarding" is a prefix of any future "viin_brand_onboarding_*" module.
MODULE_MARKER_RE = brand_marker_re(MODULE)

# The compiled chunk Odoo emits for BRAND_STYLESHEET: everything between this
# module's marker and the next file's marker. Comments inside a stylesheet are
# stripped before the header is prepended (StylesheetAsset.minify), so the next
# "/* " in the served CSS is always the next file's header.
BRAND_CHUNK_RE = re.compile(
    r"/\* %s \*/(.*?)(?:/\* |$)" % re.escape(BRAND_STYLESHEET), re.S
)


@tagged("-at_install", "post_install")
class TestBrandCssOutOfCoreTestBundles(BrandBundleCssMixin, HttpCase):
    """Brand CSS must reach the real webclient and NOTHING ELSE.

    This module's SCSS reaches core's two JS unit-test bundles the same way
    every other brand module's did - both carry ('include', 'web.assets_backend')
    (addons/web/__manifest__.py) - but with one extra consequence: the brand
    variables it consumes are defined in viin_brand_common's
    primary_variables.scss, which those bundles no longer carry. The SCSS
    therefore does not merely leak into core's test page, it kills the page:
    `Undefined variable: "$brand-primary-light"` aborts the compile of the whole
    bundle (runbot build rb-fb7185e-224180).

    So the separation is asserted in both directions, as for viin_brand_common:

    * core's JS unit-test page must compile, with none of this module's
      stylesheets in it, so core's tests measure core rather than Viindoo;
    * the real webclient must still receive this module's stylesheet, with its
      gradient rules intact, so the user's onboarding panels keep their Viindoo
      identity.

    A test that only checked the first direction would go green if somebody
    "fixed" the red compile by deleting the offending SCSS - or by deleting the
    five brand variables it reads, which is the cheaper and likelier of the two.

    Both assertions read the CSS a browser is actually served, over HTTP, at the
    bundle's real hashed URL, through BrandBundleCssMixin._fetch_bundle_css -
    which refuses to interpret a bundle that did not compile. Reading the source
    files instead, or asserting only on absence, reports success on a broken
    build: a failed compile makes Odoo serve the PREVIOUS bundle or an error
    stylesheet, and neither carries this module's markers either.
    """

    def test_brand_stylesheets_are_absent_from_core_unit_test_bundles(self):
        """No stylesheet of this module may reach core's unit-test pages.

        Asserted as "none of this module's files", not as the one file it ships
        today: the contract is that the whole module stays out. Naming the file
        would keep passing the day somebody adds a second brand stylesheet to
        web.assets_backend and forgets the matching removal - which is the exact
        regression this test exists to catch, and exactly how this module came
        to be the one brand module the earlier sweep missed.
        """
        for bundle_name in CORE_TEST_BUNDLES:
            with self.subTest(bundle=bundle_name):
                url, css = self._fetch_bundle_css(bundle_name)
                leaked = sorted(set(MODULE_MARKER_RE.findall(css)))
                self.assertFalse(
                    leaked,
                    "%s (served at %s) still compiles %d stylesheet(s) of %s "
                    "into core's unit-test page: %s. Those stylesheets read "
                    "brand variables this bundle does not define, so they do "
                    "not just leak Viindoo's design tokens into core's tests - "
                    "they abort the compile of the entire bundle."
                    % (bundle_name, url, len(leaked), MODULE, ", ".join(leaked)),
                )

    def test_brand_stylesheet_is_still_served_to_the_real_webclient(self):
        """Removing brand CSS from the TEST page must not touch the product.

        This is the assertion that stops the separation being "achieved" by
        dropping the branding: it fails the moment a removal directive is aimed
        at the webclient bundle rather than the test ones, or the stylesheet is
        dropped from the manifest altogether.
        """
        url, css = self._fetch_bundle_css(WEBCLIENT_BUNDLE)
        self.assertIn(
            "/* %s */" % BRAND_STYLESHEET,
            css,
            "%s (served at %s) no longer compiles %s. The real webclient must "
            "keep this module's stylesheet - only the unit-test bundles lose "
            "it." % (WEBCLIENT_BUNDLE, url, BRAND_STYLESHEET),
        )

    def test_onboarding_panels_keep_their_brand_gradient_in_the_webclient(self):
        """The onboarding panels must still be painted with a brand gradient.

        The marker asserted above proves the file was concatenated into the
        webclient bundle; it does NOT prove the file still produces any CSS,
        because Odoo emits the marker for an empty compiled chunk just the same.
        That gap matters here specifically: the cheapest wrong fix for the red
        compile is to delete the five brand variables this stylesheet reads,
        which leaves the marker in place, the bundle compiling, and the product
        silently unbranded. So assert the chunk this module contributes actually
        carries its gradient declarations.

        Asserted as "a gradient is produced", not as a computed colour value:
        the brand colours are derived through lighten()/darken()/fade-out(), and
        pinning the arithmetic's output would fail on a legitimate palette
        change while proving nothing more about the rule being protected.
        """
        url, css = self._fetch_bundle_css(WEBCLIENT_BUNDLE)
        chunk = BRAND_CHUNK_RE.search(css)
        self.assertTrue(
            chunk,
            "%s (served at %s) carries no compiled chunk for %s at all."
            % (WEBCLIENT_BUNDLE, url, BRAND_STYLESHEET),
        )
        self.assertIn(
            "linear-gradient(",
            chunk.group(1),
            "%s (served at %s) compiles %s to CSS that declares no gradient. "
            "The onboarding panels are branded by exactly one mechanism - the "
            "o-onboarding-vertical-gradient mixin fed with the brand palette - "
            "so a chunk with no gradient in it means the panels lost their "
            "Viindoo identity, whatever else still compiles."
            % (WEBCLIENT_BUNDLE, url, BRAND_STYLESHEET),
        )
