import logging
import re

_logger = logging.getLogger(__name__)

# The two bundles core's own JS unit tests are served from. Both pull in
# web.assets_backend with ('include', ...) (addons/web/__manifest__.py), which is
# how brand SCSS reaches them in the first place - and why every brand module
# that contributes to web.assets_backend needs its own ('remove', ...) pair.
CORE_TEST_BUNDLES = ("web.assets_unit_tests_setup", "web.tests_assets")

# The bundle the real webclient is served from - the counterweight side of the
# same contract. It carries ('include', 'web.assets_backend') too, so anything
# removed from the test bundles must still be found here.
WEBCLIENT_BUNDLE = "web.assets_web"

# --- non-vacuity witnesses --------------------------------------------------
#
# A failed SCSS compile does NOT make Odoo serve nothing. AssetsBundle.css()
# (odoo/addons/base/models/assetsbundle.py) throws the freshly compiled output
# away and serves the PREVIOUS attachment - empty on a fresh database - followed
# by this header and a `css_error_message` rule carrying the compiler's message.
# The served stylesheet then contains the markers of NO module at all, so an
# absence-only assertion reports success at the exact moment the bundle is
# broken. That is not hypothetical: runbot build rb-fb7185e-224180 shipped that
# false pass while `Undefined variable: "$brand-primary-light"` was killing the
# whole bundle. Every read of a bundle must therefore prove the bundle really
# compiled BEFORE anything is concluded from what is missing from it.
CSS_COMPILE_ERROR_HEADER = "/* ## CSS error message ##*/"
CSS_COMPILE_ERROR_RE = re.compile(
    r'css_error_message\s*\{\s*content:\s*"(.*?)"\s*;?\s*\}', re.S
)

# Odoo prefixes every stylesheet it concatenates with a comment naming that file
# (StylesheetAsset.with_header). A bundle that includes web.assets_backend
# therefore always carries core's own stylesheet markers when it compiled, and
# carries none of them when it did not. This is the POSITIVE half of the
# witness: it is what separates "compiled fine, our CSS correctly absent" from
# "compiled to nothing, everything absent". Only valid for bundles that include
# web.assets_backend - which is true of CORE_TEST_BUNDLES and WEBCLIENT_BUNDLE
# alike.
CORE_STYLESHEET_MARKER_RE = re.compile(r"/\* (/web/static/[^*]*\.s?css) \*/")


def brand_marker_re(module):
    """Return the regex matching every stylesheet marker owned by ``module``.

    Matching on the FULL comment - "/* " then a leading slash then the module
    name then a slash - and never on the bare module name is load-bearing: a
    bare substring search for "web_responsive" also matches
    "viin_customizer_web_responsive", and a bare search for any module name
    equally matches any module holding it as a prefix or a suffix. Anchoring on
    both sides is what keeps "viin_brand_onboarding" from matching a future
    "viin_brand_onboarding_extra". That mistake produces a red run with nothing
    wrong, which is worse than no test.
    """
    return re.compile(r"/\* (/%s/[^*]*) \*/" % re.escape(module))


def readable_css_error(css):
    """Return the compiler message Odoo escaped into the error stylesheet."""
    match = CSS_COMPILE_ERROR_RE.search(css)
    if not match:
        return "<no css_error_message rule in the served stylesheet>"
    # css() escapes the message for a CSS string: newlines become \A, '*'
    # becomes \* so it cannot close the comment, and '"' is backslash-escaped.
    return (
        match.group(1)
        .replace(r"\A", "\n")
        .replace(r"\*", "*")
        .replace(r"\"", '"')
    )


class BrandBundleCssMixin:
    """Read an asset bundle's CSS as a browser is actually served it.

    Plain mixin on purpose, not a TestCase: Odoo collects only members of a
    tests package whose name starts with "test_"
    (odoo/tests/loader.py _get_tests_modules), so this file is importable from a
    dependent module's tests without its contents being collected twice.
    """

    def _fetch_bundle_css(self, bundle_name):
        """Return ``(url, css)`` for ``bundle_name`` as actually served.

        Reading the served bytes rather than the source files is what makes the
        assertions built on top immune to the stale-bundle trap: when an SCSS
        edit breaks compilation, Odoo keeps serving the previous bundle and an
        inspection of the source files alone reports success.
        """
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
        self._assert_bundle_really_compiled(bundle_name, url, css)
        _logger.info(
            "[brand-css-guard] %s served from %s (%d bytes, %d core stylesheet markers)",
            bundle_name,
            url,
            len(response.content),
            len(CORE_STYLESHEET_MARKER_RE.findall(css)),
        )
        return url, css

    def _assert_bundle_really_compiled(self, bundle_name, url, css):
        """Fail unless the served stylesheet is the product of a real compile.

        Without this, "our markers are absent" is indistinguishable from "the
        bundle is a compile-error stub and EVERYTHING is absent" - and the
        second one goes green. Both halves are needed: the error header catches
        a failed compile that still served a stale previous bundle, the core
        markers catch a failed compile that served nothing to be stale.
        """
        self.assertNotIn(
            CSS_COMPILE_ERROR_HEADER,
            css,
            "%s (served at %s) is a compile-error stylesheet, not a compiled "
            "bundle. Nothing may be concluded from what is or is not in it - "
            "in particular, no absence assertion over it means anything. The "
            "SCSS compiler said:\n%s" % (bundle_name, url, readable_css_error(css)),
        )
        self.assertTrue(
            CORE_STYLESHEET_MARKER_RE.search(css),
            "%s (served at %s) carries not one core stylesheet marker, so it "
            "cannot be the product of a successful compile of a bundle that "
            "includes web.assets_backend. Any absence assertion over this "
            "stylesheet would pass for the wrong reason." % (bundle_name, url),
        )
