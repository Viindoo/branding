# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Odoo does not check at install that a bare (untargeted) manifest asset entry resolves to a
# file. A missing file only surfaces when the bundle is built, as an error that names the asset
# (`in file '<path>'`): in `css_errors` for a stylesheet, as an embedded `console.error(...)`
# for JS and an embedded `throw new Error(...)` for an XML template. None of them raises out of
# `.css()` / `.js()`, so each check looks for the asset's own path in the compiled payload.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every asset bundle this module contributes to must actually resolve and compile clean."""

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        return bundle, css

    def _compiled_js(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=False, js=True)
        js_attachment = bundle.js()
        content = (js_attachment.raw or b"").decode("utf-8", "replace") if js_attachment else ""
        return js_attachment, content

    def _own_asset_error_marker(self, asset_path):
        """The literal Odoo embeds in a compiled bundle when `asset_path` itself failed.

        A bare phrase such as "throw new Error(" would also match core files in the same bundle.
        """
        return "in file '%s'" % asset_path

    def test_backend_bundle_compiles_the_viindoo_logo_overrides(self):
        """web.assets_backend carries the Viindoo-logo SCSS override with no Sass fault."""
        bundle, css = self._compiled_css("web.assets_backend")
        self.assertFalse(
            bundle.css_errors,
            "web.assets_backend reported SCSS compile errors: %s" % "; ".join(bundle.css_errors),
        )
        self.assertIn(
            "/viin_brand/static/img/Viindoo-logo.svg",
            css,
            "web.assets_backend compiled without the Viindoo logo override from "
            "website_loader.scss.",
        )

    def test_editor_bundle_compiles_the_resource_editor_warning_extension(self):
        """website.assets_editor extends website.ResourceEditorWarningOverlay cleanly."""
        _js_attachment, content = self._compiled_js("website.assets_editor")
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/src/components/resource_editor/"
                "resource_editor_warning.xml"
            ),
            content,
            "website.assets_editor compiled with an embedded template error - "
            "resource_editor_warning.xml failed to resolve or parse.",
        )
        self.assertIn(
            "website.ResourceEditorWarningOverlay",
            content,
            "website.assets_editor compiled without the ResourceEditorWarningOverlay extension "
            "from resource_editor_warning.xml.",
        )

    def test_website_builder_assets_bundle_compiles_the_info_option_extension(self):
        """website.website_builder_assets extends website.InfoPageOption cleanly."""
        _js_attachment, content = self._compiled_js("website.website_builder_assets")
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/src/builder/plugins/options/website_info_option.xml"
            ),
            content,
            "website.website_builder_assets compiled with an embedded template error - "
            "website_info_option.xml failed to resolve or parse.",
        )
        self.assertIn(
            "website.InfoPageOption",
            content,
            "website.website_builder_assets compiled without the InfoPageOption extension from "
            "website_info_option.xml.",
        )

    def test_editor_bundle_compiles_the_seo_keywords_help_extension(self):
        """website.assets_editor drops the odoo.com link of the SEO keywords help cleanly."""
        _js_attachment, content = self._compiled_js("website.assets_editor")
        self.assertNotIn(
            self._own_asset_error_marker("viin_brand_website/static/src/components/dialog/seo_brand.xml"),
            content,
            "website.assets_editor compiled with an embedded template error - seo_brand.xml failed "
            "to resolve or parse.",
        )
        self.assertRegex(
            content,
            r'registerTemplateExtension\(\s*"website\.seoMetaKeywordsDocumentationLink",\s*`[^`]*seo_brand\.xml`',
        )

    def test_builder_iframe_bundle_carries_the_countdown_end_message_extension(self):
        """The countdown end message lives in the iframe bundle, so its extension must too."""
        _js_attachment, content = self._compiled_js("website.assets_inside_builder_iframe")
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/src/builder/plugins/options/countdown_brand.edit.xml"
            ),
            content,
            "website.assets_inside_builder_iframe compiled with an embedded template error - "
            "countdown_brand.edit.xml failed to resolve or parse.",
        )
        self.assertRegex(
            content,
            r'registerTemplateExtension\(\s*"website\.s_countdown\.end_message",\s*`[^`]*countdown_brand\.edit\.xml`',
        )

    def test_website_builder_assets_bundle_carries_the_facebook_page_default(self):
        """website.website_builder_assets patches the Facebook option plugin with the Viindoo page."""
        _js_attachment, content = self._compiled_js("website.website_builder_assets")
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/src/builder/plugins/options/facebook_option_plugin.js"
            ),
            content,
            "website.website_builder_assets compiled with an embedded error for "
            "facebook_option_plugin.js.",
        )
        self.assertIn("@viin_brand_website/builder/plugins/options/facebook_option_plugin", content)

    def test_frontend_bundle_delivers_the_apps_button_click_wiring_to_the_browser(self):
        """web.assets_frontend carries the apps button's click wiring, not just its file.

        The button is a sibling of #wrapwrap, so it is wired through document-level click and
        auxclick listeners at load time; the compiled payload must bind both.
        """
        js_attachment, content = self._compiled_js("web.assets_frontend")
        self.assertTrue(
            js_attachment,
            "web.assets_frontend did not produce a JS attachment - the bundle did not build.",
        )
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/src/js/frontend_to_backend_apps_btn.js"
            ),
            content,
            "web.assets_frontend compiled with a missing-asset error for "
            "frontend_to_backend_apps_btn.js.",
        )
        # Whitespace-insensitive: a production bundle is minified.
        for event_type in ("click", "auxclick"):
            self.assertRegex(
                content,
                r'addEventListener\(\s*"%s"\s*,\s*onAppsBtnClick\s*\)' % event_type,
                "web.assets_frontend compiled without the apps button's %r listener binding"
                % event_type,
            )

    def test_tests_bundle_compiles_the_apps_button_wiring_tour(self):
        """web.assets_tests carries the apps-button wiring tour."""
        js_attachment, content = self._compiled_js("web.assets_tests")
        self.assertTrue(
            js_attachment,
            "web.assets_tests did not produce a JS attachment - the bundle did not build.",
        )
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/tests/tours/frontend_to_backend_apps_btn_wiring.js"
            ),
            content,
            "web.assets_tests compiled with a missing-asset error for "
            "frontend_to_backend_apps_btn_wiring.js.",
        )
        self.assertIn(
            "viin_brand_website_frontend_to_backend_apps_btn_wiring",
            content,
            "web.assets_tests compiled without the apps-button wiring tour from "
            "frontend_to_backend_apps_btn_wiring.js.",
        )
