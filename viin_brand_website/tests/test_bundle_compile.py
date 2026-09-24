# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Every bundle this module contributes to must resolve every file it lists and compile with no
# error. Odoo never checks this at install: a bare (untargeted) manifest entry whose file is
# missing on disk resolves through `IrAsset._get_paths` (ir_asset.py) to a placeholder
# with NO filename, no exception. The failure only surfaces once something tries to read that
# asset's content: `WebAsset.stat()` (assetsbundle.py) then falls through to an
# ir.attachment lookup, which also misses and raises `AssetNotFound("Could not find %s" %
# self.name)`; back in `WebAsset._fetch_content` (assetsbundle.py) that exception is not
# an `IOError`, so it is re-wrapped by the bare `except:` clause into
# `AssetError('Could not get content for %s.' % self.name)`. A stylesheet asset folds that into
# `bundle.css_errors` (`StylesheetAsset._fetch_content`, assetsbundle.py). A javascript OR an
# XML/OWL template asset instead routes it through `WebAsset.generate_error` (assetsbundle.py),
# which ALWAYS wraps the message as `f'{msg!r} in file {self.url!r}'` before a javascript asset
# embeds it in a swallowed `console.error(...)` call (`JavascriptAsset.generate_error`,
# assetsbundle.py) and an XML asset instead raises `XMLAssetError`, caught one level up by
# `AssetsBundle.generate_xml_bundle` (assetsbundle.py) and embedded as a `throw new Error(...)`
# statement in the compiled JS
# payload. Neither shape raises out of a bare `.css()` / `.js()` call, so "the call did not raise"
# proves nothing; and a BARE phrase like "does not exist" or "throw new Error(" is unsafe too - it
# collides with unrelated core files' own legitimate content compiled into the same shared bundle.
# The one substring every one of these wrapped messages carries, and only for the asset that
# actually failed, is `in file '<that asset's own resolved path>'` - so each JS/XML channel check
# below is scoped to that asset's own path, never a bare phrase over the whole bundle.
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
        """The literal Odoo embeds into a compiled bundle when `asset_path` itself is the asset
        that failed - see the module comment for the exact wrapping chain. Scoping to this
        asset's own resolved path (rather than a bare phrase such as "does not exist" or
        "throw new Error(") is what keeps the check from tripping on unrelated core files'
        legitimate content compiled into the same shared bundle."""
        return "in file '%s'" % asset_path

    def test_backend_bundle_compiles_the_viindoo_logo_overrides(self):
        """web.assets_backend must carry both Viindoo-logo SCSS overrides with no Sass fault.

        WOULD FAIL IF: configurator.scss or website_loader.scss is renamed or deleted (the bare
        manifest entry then resolves with no filename, and fetching its content raises
        AssetNotFound into bundle.css_errors - see the module comment), or either file develops a
        genuine Sass fault.
        """
        bundle, css = self._compiled_css("web.assets_backend")
        self.assertFalse(
            bundle.css_errors,
            "web.assets_backend reported SCSS compile errors: %s" % "; ".join(bundle.css_errors),
        )
        self.assertIn(
            "/viin_brand/static/img/Viindoo-logo.svg",
            css,
            "web.assets_backend compiled without the Viindoo logo override from "
            "configurator.scss / website_loader.scss.",
        )

    def test_editor_bundle_compiles_the_resource_editor_warning_extension(self):
        """website.assets_editor must extend website.ResourceEditorWarningOverlay cleanly.

        WOULD FAIL IF: resource_editor_warning.xml is renamed, deleted, develops malformed XML, or
        its `t-inherit` target stops existing - every one of those shapes is folded into an
        embedded `throw new Error(...)` statement carrying this file's own path (see the module
        comment), rather than a raised exception, so this reads the compiled payload instead of
        trusting a bare "did not raise".
        """
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
        """website.website_builder_assets must extend website.InfoPageOption cleanly.

        WOULD FAIL IF: website_info_option.xml is renamed, deleted, develops malformed XML, or its
        `t-inherit` target stops existing - the same embedded-throw failure shape as the editor
        bundle above, carrying this file's own path.
        """
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

    def test_frontend_bundle_delivers_the_apps_button_click_wiring_to_the_browser(self):
        """web.assets_frontend must actually carry the apps-button's live click wiring, not just
        its file.

        Business rule: a unit-tested pure function nobody ever loads protects nothing - the
        frontend header's apps button is only ever rendered for an authenticated internal user
        (website.layout's own `groups="base.group_user"` guard), but the bundle that must carry
        its behaviour is `web.assets_frontend`, downloaded on every website page regardless of who
        is looking at it. The button is a #wrapwrap SIBLING, never a descendant, so it cannot be
        wired through `public.interactions` (that service only ever scans #wrapwrap, or body when
        #wrapwrap is absent); the module instead binds document-level click/auxclick listeners at
        load time. This asserts the compiled payload actually carries BOTH bindings, not merely
        that a source file exists on disk - a manifest entry naming a file that defines the
        handler but never calls `addEventListener` with it would still compile clean and still
        fail this.

        WOULD FAIL IF: frontend_to_backend_apps_btn.js is renamed, deleted, or its manifest entry
        never added (the missing/unlisted file surfaces as a swallowed console.error carrying this
        file's own path rather than a raised exception - see the module comment), OR the file
        exists but its listener registration is dropped for either event.
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
            "web.assets_frontend compiled with a swallowed missing-asset error embedded as a "
            "console.error call - frontend_to_backend_apps_btn.js is missing or was never added "
            "to the manifest's web.assets_frontend entry.",
        )
        # Whitespace-insensitive: a production (non-debug) bundle compiles through a minifier
        # that strips spacing, so an exact-spacing literal would only ever match a debug build.
        for event_type in ("click", "auxclick"):
            self.assertRegex(
                content,
                r'addEventListener\(\s*"%s"\s*,\s*onAppsBtnClick\s*\)' % event_type,
                "web.assets_frontend compiled without the apps button's %r listener binding - "
                "frontend_to_backend_apps_btn.js did not load or dropped that binding."
                % event_type,
            )

    def test_tests_bundle_compiles_the_apps_button_wiring_tour(self):
        """web.assets_tests must carry the apps-button wiring tour with no missing file.

        WOULD FAIL IF: frontend_to_backend_apps_btn_wiring.js is renamed or deleted - the missing
        file is swallowed into an embedded `console.error(...)` string carrying this file's own
        path rather than raised, so a bare "did not raise" would stay green; or a genuine JS
        syntax fault, which does raise uncaught from the ES-module transpile step.
        """
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
            "web.assets_tests compiled with a swallowed missing-asset error embedded as a "
            "console.error call - frontend_to_backend_apps_btn_wiring.js no longer exists on disk.",
        )
        self.assertIn(
            "viin_brand_website_frontend_to_backend_apps_btn_wiring",
            content,
            "web.assets_tests compiled without the apps-button wiring tour from "
            "frontend_to_backend_apps_btn_wiring.js.",
        )

    def test_tests_bundle_compiles_the_colorpicker_override_tour(self):
        """web.assets_tests must carry the branded colorpicker tour override with no missing file.

        WOULD FAIL IF: colorpicker_brand_override.js is renamed or deleted - the missing file is
        swallowed into an embedded `console.error(...)` string carrying this file's own path
        rather than raised, so a bare "did not raise" would stay green; or a genuine JS syntax
        fault, which does raise uncaught from the ES-module transpile step.
        """
        js_attachment, content = self._compiled_js("web.assets_tests")
        self.assertTrue(
            js_attachment,
            "web.assets_tests did not produce a JS attachment - the bundle did not build.",
        )
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_website/static/tests/tours/colorpicker_brand_override.js"
            ),
            content,
            "web.assets_tests compiled with a swallowed missing-asset error embedded as a "
            "console.error call - colorpicker_brand_override.js no longer exists on disk.",
        )
        self.assertIn(
            "website_background_colorpicker",
            content,
            "web.assets_tests compiled without the branded colorpicker tour override from "
            "colorpicker_brand_override.js.",
        )
