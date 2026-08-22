# Copyright 2026 Viindoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import re

from odoo.tests.common import HttpCase, tagged

_logger = logging.getLogger(__name__)

MODULE = "web_responsive"

# The two bundles core's own JS unit tests are served from. Both pull in
# web.assets_backend with ('include', ...) (addons/web/__manifest__.py), which
# is how this module's SCSS used to reach them in the first place.
CORE_TEST_BUNDLES = ("web.assets_unit_tests_setup", "web.tests_assets")

# The bundle the real webclient is served from - the counterweight side of the
# same contract.
WEBCLIENT_BUNDLE = "web.assets_web"

# The stylesheet carrying this module's responsive backend layout - the form
# sheet margins and paddings that core's own mobile-viewport tests were
# measuring instead of core's own layout. If it stops reaching the real
# webclient, the responsive layout this module exists to provide is gone.
LAYOUT_STYLESHEET = "/%s/static/src/legacy/scss/web_responsive.scss" % MODULE

# Odoo's SCSS compiler prefixes every source file it concatenates with a
# comment naming that file's path. Matching the FULL comment - "/* " then a
# LEADING SLASH then the module name - rather than the bare module name is
# load-bearing here and not a stylistic preference: this database also carries
# `viin_customizer_web_responsive`, whose own stylesheet legitimately sits in
# the unit-test bundle. A bare substring search for "web_responsive" matches it
# and reports a leak that does not exist - a red run with nothing wrong behind
# it, which costs more trust than no test at all.
MODULE_MARKER_RE = re.compile(r"/\* (/%s/[^*]*) \*/" % re.escape(MODULE))


@tagged("-at_install", "post_install")
class TestWebResponsiveCssOutOfCoreTestBundles(HttpCase):
    """This module's CSS must reach the real webclient and NOTHING ELSE.

    ``web_responsive`` restyles the backend layout, and core's own JS unit
    tests measure backend layout geometry. While this module's SCSS was
    compiled into core's unit-test page, those tests were measuring
    web_responsive's layout and calling core wrong for it. The manifest now
    removes each of this module's stylesheets from the two test bundles.

    Both directions of that separation are asserted, because a test that only
    checked the first one would go green if somebody "fixed" a red run by
    deleting the responsive stylesheets outright:

    * core's unit-test pages must compile without any stylesheet of this
      module;
    * the real webclient must still receive them.

    The assertions read the CSS a browser is actually served, over HTTP, at the
    bundle's real hashed URL. That matters: when an SCSS edit breaks
    compilation Odoo keeps serving the PREVIOUS bundle, so anything that
    inspects source files rather than served bytes reports success on a broken
    tree.
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
            "[web-responsive-css-guard] %s served from %s (%d bytes)",
            bundle_name,
            url,
            len(response.content),
        )
        return url, css

    def test_module_stylesheets_are_absent_from_core_unit_test_bundles(self):
        """No stylesheet of this module may reach core's unit-test pages.

        Asserted as "none of this module's files", not as one named file: the
        contract is that the whole set stays out. Listing files instead would
        keep passing the day somebody adds a new stylesheet to
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
                    "into core's unit-test page: %s. Core's own layout tests "
                    "then measure this module's geometry instead of core's."
                    % (bundle_name, url, len(leaked), MODULE, ", ".join(leaked)),
                )

    def test_module_stylesheets_are_still_served_to_the_real_webclient(self):
        """Removing this CSS from the TEST page must not touch the product.

        This is the assertion that stops the separation being "achieved" by
        dropping the responsive layout altogether: it fails the moment a
        removal directive is aimed at the webclient bundle rather than the test
        ones.
        """
        url, css = self._fetch_bundle_css(WEBCLIENT_BUNDLE)
        self.assertIn(
            "/* %s */" % LAYOUT_STYLESHEET,
            css,
            "%s (served at %s) no longer compiles %s. The real webclient must "
            "keep the responsive layout - only the unit-test bundles lose it."
            % (WEBCLIENT_BUNDLE, url, LAYOUT_STYLESHEET),
        )
