# D2-A bundle-compile requirement - protects the business rule: "the JS file this module
# contributes to im_livechat.embed_assets_unit_tests actually lands in the compiled bundle."
# Odoo validates this NEITHER at install time NOR at manifest-parse time: the manifest entry below
# carries no `before`/`after`/`replace` directive, so AssetPaths.index() (ir_asset.py) - the only
# place a dangling asset reference ever raises ValueError - never runs its anchor check against it;
# a bare append instead resolves through a plain filesystem glob with no existence check. A renamed
# or deleted file just drops silently out of the resolved list, the bundle still "compiles"
# successfully without it, and no `-i`/`-u` run ever notices (no `ir_asset` symbol is referenced
# anywhere in odoo/modules/loading.py or odoo/modules/registry.py). Only asserting this module's
# OWN content actually landed in the compiled output - not merely that the bundle built - proves
# the wiring.
from odoo.tests.common import TransactionCase, tagged

BUNDLE_NAME = "im_livechat.embed_assets_unit_tests"

# The exact `test()` description this module's own
# static/tests/embed/livechat_button_debrand.test.js declares. That file is a bare manifest append
# with no anchor, so a rename or removal drops it silently out of the compiled bundle (see the
# module docstring) instead of raising. The string is unique across every file this bundle draws
# from (this module's own contribution plus core's `web/static/tests/_framework/**/*` and
# `im_livechat/static/tests/embed/**/*`), so its presence in the compiled JS unambiguously proves
# this module's file - not a core one - landed in the bundle. It also survives the ES-module
# transpile step verbatim: that step only rewrites import/export syntax, never string content.
_CONTRIBUTED_TEST_MARKER = (
    "the livechat launcher button must render without throwing, even with the module's own "
    "style override active"
)


@tagged("post_install", "-at_install")
class TestImLivechatBundleCompile(TransactionCase):
    """This module's only contributed bundle must actually carry this module's own JS."""

    def test_embed_assets_unit_tests_bundle_carries_this_modules_debrand_test(self):
        """im_livechat.embed_assets_unit_tests compiles with this module's own test file inside it.

        WOULD FAIL IF: `static/tests/embed/livechat_button_debrand.test.js` is renamed or removed
        without updating the manifest's `im_livechat.embed_assets_unit_tests` entry - a bare
        append with no anchor, so the stale path drops out of the resolved glob with no exception
        (see module docstring) and the marker below goes missing from the compiled output; OR a JS
        syntax fault in that file, which raises uncaught from the ES-module transpile step when the
        bundle actually builds, failing this test outright before the assertion below runs.
        """
        bundle = self.env["ir.qweb"]._get_asset_bundle(BUNDLE_NAME, css=False, js=True)
        attachment = bundle.js()
        self.assertTrue(
            attachment,
            "%s did not produce a JS attachment - the bundle did not build." % BUNDLE_NAME,
        )
        js = (attachment.raw or b"").decode("utf-8", "replace")
        self.assertIn(
            _CONTRIBUTED_TEST_MARKER, js,
            "%s compiled without viin_brand_im_livechat's own contributed test file - its "
            "manifest entry may have gone stale (renamed/removed source) or the file dropped out "
            "of the bundle silently." % BUNDLE_NAME,
        )


# im_livechat.assets_embed_core declares no Sass helpers/variables of its own, so compiling it in
# isolation errors for reasons that have nothing to do with any contributor - a permanently-red,
# non-diagnostic oracle. im_livechat.assets_embed_external is the real compiled unit that
# ('include's it alongside web's Sass-helper bundles, and is what the embed actually serves.
LIVECHAT_EMBED_COMPILED_BUNDLE = "im_livechat.assets_embed_external"

# assetsbundle.py bakes these three literal markers into the fallback stylesheet it ships when a
# bundle's compile fails; `.css()` returns an already-cached attachment WITHOUT repopulating
# `css_errors`, so an empty `css_errors` list alone cannot tell a clean compile from a stale cached
# failure - only a payload scan can.
_CACHED_CSS_ERROR_MARKERS = ("## CSS error message ##", "css_error_message", "A css error occured")

# This module's own manifest entry into `im_livechat.assets_embed_core` shares its four SCSS
# source files with another module's own bundle entry elsewhere (the physical files are not this
# module's to move). A marker proving the CONTENT actually landed - not merely that the bundle
# built clean - therefore has to come from one of those four files, be a selector or declaration
# fragment rather than a colour literal (every value on this ladder is subject to AA re-tuning),
# and be absent from core im_livechat's own SCSS. The chatter customer-facing composer selector
# below qualifies on all three counts: core's own composer carries no per-mode chrome at all (it
# reads `props.type` only for label/placeholder/subtype text, never for a class or a CSS custom
# property), so this exact selector chain cannot originate from core im_livechat or core mail.
_OWN_SCSS_CONTRIBUTION_MARKER = ".o-mail-Chatter-top:has(.o-mail-Chatter-sendMessage.active)"


class TestImLivechatEmbedCssBundleOwnership(TransactionCase):
    """The compiled livechat embed CSS must carry this module's OWN branding contribution."""

    def test_assets_embed_core_entry_lands_this_modules_branding_in_the_compiled_embed_bundle(self):
        """The livechat embed surface gets Viindoo's skin from THIS module's own manifest entry.

        WOULD FAIL IF: this module's `im_livechat.assets_embed_core` manifest entry, or its
        dependency on the module whose static folder physically hosts the four contributed SCSS
        files, went missing - either way the marker below would drop out of the compiled
        `im_livechat.assets_embed_external` output. `im_livechat`'s own dependency closure (mail,
        rating, digest, utm) never reaches that module, so nothing else pulls the branding in for
        a database that installs only `im_livechat` plus this module - the marker landing here can
        only be this module's own declared contribution, never an incidental reach.
        """
        bundle = self.env["ir.qweb"]._get_asset_bundle(
            LIVECHAT_EMBED_COMPILED_BUNDLE, css=True, js=False
        )
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertFalse(
            bundle.css_errors,
            "%s compiled with CSS errors (expected none): %s"
            % (LIVECHAT_EMBED_COMPILED_BUNDLE, bundle.css_errors),
        )
        self.assertTrue(
            css.strip(), "%s compiled to empty CSS." % LIVECHAT_EMBED_COMPILED_BUNDLE,
        )
        for marker in _CACHED_CSS_ERROR_MARKERS:
            self.assertNotIn(
                marker, css,
                "%s served a cached CSS-error fallback payload (marker %r found) - an earlier "
                "compile failed and this one only looked clean because css() returned the "
                "cached attachment without repopulating css_errors."
                % (LIVECHAT_EMBED_COMPILED_BUNDLE, marker),
            )
        self.assertIn(
            _OWN_SCSS_CONTRIBUTION_MARKER, css,
            "%s compiled without this module's own branding contribution - its "
            "im_livechat.assets_embed_core manifest entry may be missing, or the dependency that "
            "hosts the contributed SCSS files may be missing." % LIVECHAT_EMBED_COMPILED_BUNDLE,
        )
