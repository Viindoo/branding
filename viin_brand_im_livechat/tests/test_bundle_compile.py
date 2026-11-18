from odoo.tests.common import TransactionCase, tagged

BUNDLE_NAME = "im_livechat.embed_assets_unit_tests"


@tagged("post_install", "-at_install")
class TestImLivechatBundleCompile(TransactionCase):
    """This module's contribution to the livechat embed test bundle lands in the compiled bundle."""

    def test_embed_assets_unit_tests_bundle_carries_this_modules_debrand_test(self):
        """im_livechat.embed_assets_unit_tests compiles with this module's own test file inside it."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(BUNDLE_NAME, css=False, js=True)
        attachment = bundle.js()
        self.assertTrue(
            attachment,
            "%s did not produce a JS attachment - the bundle did not build." % BUNDLE_NAME,
        )
        js = (attachment.raw or b"").decode("utf-8", "replace")
        # The description of the test in static/tests/embed/livechat_button_debrand.test.js. Its
        # manifest entry has no `before`/`after`/`replace` anchor, so a renamed or deleted file
        # drops out of the bundle without any error.
        self.assertIn(
            "the livechat launcher button renders without throwing with the module's embed "
            "assets loaded", js,
            "%s compiled without viin_brand_im_livechat's own contributed test file - its "
            "manifest entry may be stale." % BUNDLE_NAME,
        )


# im_livechat.assets_embed_core declares no Sass helpers, so it does not compile on its own;
# im_livechat.assets_embed_external includes it with the Sass helpers and is what the embed serves.
LIVECHAT_EMBED_COMPILED_BUNDLE = "im_livechat.assets_embed_external"


class TestImLivechatEmbedCssBundleOwnership(TransactionCase):
    """The compiled livechat embed CSS carries this module's own branding contribution."""

    def test_assets_embed_core_entry_lands_this_modules_branding_in_the_compiled_embed_bundle(self):
        """The livechat embed surface gets Viindoo's skin from this module's manifest entry.

        The dependency closure of `im_livechat` does not reach the module that hosts the SCSS
        files, so the marker only lands through this module's own entry and dependency.
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
        # The fallback stylesheet of a failed compile carries these markers. `.css()` returns an
        # already cached attachment without repopulating `css_errors`, so only the payload tells a
        # clean compile from a cached failure.
        for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
            self.assertNotIn(
                marker, css,
                "%s served a cached CSS-error fallback payload (marker %r found)"
                % (LIVECHAT_EMBED_COMPILED_BUNDLE, marker),
            )
        # A selector of the SCSS files this module adds to `im_livechat.assets_embed_core`: it is
        # absent from core's own SCSS, and a selector survives colour changes.
        self.assertIn(
            ".o-mail-Chatter-top:has(.o-mail-Chatter-sendMessage.active)", css,
            "%s compiled without this module's own branding contribution"
            % LIVECHAT_EMBED_COMPILED_BUNDLE,
        )
