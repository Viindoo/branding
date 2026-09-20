# D2-A bundle-compile requirement (the "asset anchors are validated lazily" finding) - protects
# the business rule: "every asset anchor and SCSS/JS contribution this module makes to a bundle
# resolves and compiles cleanly." Odoo validates NEITHER at install time, verified against
# odoo/addons/base/models/:
#   * a ('before'/'after'/'replace', anchor, source) directive resolves its ANCHOR through
#     AssetPaths.index() (ir_asset.py:396), called from _process_path (ir_asset.py:229) on every
#     _get_asset_paths() run (ir_asset.py:129) - a renamed/removed anchor makes it raise
#     ValueError("File(s) ... not found in bundle ...") (ir_asset.py:431, _raise_not_found). This
#     only happens when a bundle is actually RESOLVED - no `ir_asset` symbol is referenced anywhere
#     in odoo/modules/loading.py or odoo/modules/registry.py, so -i/-u never triggers it;
#   * a CONTRIBUTED file that is missing or malformed surfaces only when its own content is
#     fetched: WebAsset._fetch_content (assetsbundle.py:774) raises AssetNotFound on a missing
#     file, which StylesheetAsset._fetch_content (assetsbundle.py:935-958) catches and appends to
#     `bundle.css_errors` instead of raising - a genuine Sass fault (undefined variable/function,
#     bad map-merge) lands in that same list;
#   * for a JS asset the same AssetNotFound is instead SWALLOWED into an embedded
#     `console.error(...)` string (JavascriptAsset.generate_error, assetsbundle.py:806-808) rather
#     than raised or recorded in any list - so a bare `bundle.js()` call that merely "does not
#     raise" is a vacuous check for a missing JS file; a real JS syntax fault still raises
#     uncaught, from the ES-module transpile step (JavascriptAsset.content, assetsbundle.py:822).
# A module with a dangling anchor or a broken SCSS/JS contribution therefore installs clean and
# only explodes - or silently degrades - the first time a browser actually asks for the bundle.
# This file is that compile, for every bundle in this module's __manifest__.py `assets` key.
#
# web._assets_primary_variables is deliberately NOT compiled standalone. This module anchors its
# own primary_variables.scss into it via `('before', 'web/static/src/scss/primary_variables.scss',
# 'viin_backend_theme/static/src/scss/primary_variables.scss')`, but web/__manifest__.py defines
# `web._assets_primary_variables` as ONLY `primary_variables.scss` + `**/*.variables.scss` - it
# never includes `web._assets_helpers`. Both core's own primary_variables.scss (twice) AND this
# module's anchored override call the Sass function `o-add-unicode-support-font()`, which is
# defined in `web/static/src/scss/utils.scss` - part of the separate `web._assets_helpers` bundle.
# Resolving `_assets_primary_variables` in isolation would therefore report an "undefined
# function" Sass error UNCONDITIONALLY, even for core's own untouched file - a defect of the
# probe, not of this module - so it would be a broken measurement, not a guard. Its anchor is
# exercised for real every time `web.assets_backend` (guarded below) compiles, since that bundle
# includes `web._assets_helpers`, which in turn includes `_assets_primary_variables`
# (web/__manifest__.py:50,383,391).
import re

from odoo.tests.common import TransactionCase, tagged

# Top-level, independently-served CSS bundles this module contributes SCSS to. Module-independence
# W3 relocation, unit 3 of 4: nocontent_helper.dark.scss (this module's last web.assets_web_dark
# entry) moved to viin_brand_web - this module's contribution to that bundle is now zero, so
# compile-testing it here would guard files this module no longer owns, not a D2-A guard on
# anything of ours.
CSS_BUNDLES = (
    "web.assets_backend",
)

# Bundles this module contributes only JS/tour files to.
JS_BUNDLES = (
    "web.assets_unit_tests",
    "web.assets_tests",
)

# The realistic failure shape for one of THIS module's own bare-append entries, traced against
# odoo/addons/base/models/: a literal (non-wildcard) missing path falls through _get_paths()
# (ir_asset.py:361-362) with full_path=None, so WebAsset.stat() (assetsbundle.py:744-751) never
# finds a filename, tries an ir.attachment lookup that ALSO misses, and raises
# AssetNotFound("Could not find %s" % self.name). AssetNotFound is NOT an IOError (it subclasses
# AssetError(Exception), assetsbundle.py:31-35), so _fetch_content()'s `except IOError:` branch
# (:786, "File %s does not exist.") is NOT what actually fires here - it falls to the bare
# `except:` (:787-788) and re-raises AssetError('Could not get content for %s.' % self.name)
# instead. So a bare "does not exist" phrase-check would not even match THIS module's own
# realistic missing-file case, on top of false-reding on unrelated content elsewhere in the bundle
# (web.assets_unit_tests / web.assets_tests also carry core's OWN files, e.g.
# base/static/tests/test_ir_model_fields_translation.js, which legitimately contains that literal
# English phrase as ordinary test content).
#
# The robust, message-agnostic signal is the wrapping every failure message ALWAYS goes through,
# regardless of which AssetError subclass or wording was raised: WebAsset.generate_error
# (assetsbundle.py:726-728) always renders `f'{msg!r} in file {self.url!r}'` - so
# "in file '<this asset's own path>'" is guaranteed present for THIS module's own failure and
# absent for anyone else's, independent of the specific message text.
_MODULE_PATH_PREFIX = "viin_backend_theme/"
_MISSING_OWN_ASSET_RE = re.compile(r"in file '" + re.escape(_MODULE_PATH_PREFIX) + r"[^']*'")


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every asset bundle this module contributes to must actually resolve and compile clean."""

    def test_css_bundles_compile_without_errors(self):
        """web.assets_backend compiles with real, error-free CSS.

        WOULD FAIL IF: the `('before', 'web/static/src/scss/primary_variables.scss',
        'viin_backend_theme/static/src/scss/primary_variables.scss')` anchor this module declares
        for `web._assets_primary_variables` is renamed or removed by a future core upgrade -
        AssetPaths.index() raises ValueError (ir_asset.py:396/431) the moment web.assets_backend
        pulls that sub-bundle in through web._assets_helpers, before this test's own assertions
        run; or a Sass fault in any of the 8 files this module lists under web.assets_backend
        (fonts.scss, editor_content_font.scss, density.scss, apps_menu_home.scss, skip_link.scss,
        home_menu.scss, skeleton.scss, appearance_systray.scss) populates `bundle.css_errors`.

        Both `css_errors` and the payload markers are checked - the same two-halves idiom this
        cluster already uses (viin_brand_web/tests/test_bundle_compile.py,
        viin_brand_mail/tests/test_mail_contrast_compile.py) - because `.css()` returns early on an
        already-cached attachment WITHOUT repopulating `css_errors`, so a bundle that failed on an
        EARLIER compile would otherwise read green here while still serving the fallback
        stylesheet (assetsbundle.py:496-511, the literal "## CSS error message ##" /
        "css_error_message" / "A css error occured" markers it bakes into that payload).
        """
        for bundle_name in CSS_BUNDLES:
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
                attachments = bundle.css() or self.env["ir.attachment"]
                css = "".join(
                    (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
                )
                self.assertFalse(
                    bundle.css_errors,
                    "%s reported SCSS compile errors: %s" % (bundle_name, "; ".join(bundle.css_errors)),
                )
                self.assertTrue(
                    css.strip(),
                    "%s compiled to empty CSS - the bundle did not build." % bundle_name,
                )
                for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
                    self.assertNotIn(
                        marker, css,
                        "%s served a CACHED CSS-error fallback payload (marker %r found) - an "
                        "earlier compile failed and the current one only looked clean because "
                        "css() returned the cached attachment without repopulating css_errors."
                        % (bundle_name, marker),
                    )

    def test_js_bundles_build_with_no_missing_or_malformed_asset(self):
        """web.assets_unit_tests / web.assets_tests resolve every listed file and build clean JS.

        WOULD FAIL IF: `static/tests/viin_theme_service.test.js` (web.assets_unit_tests) or any of
        the 6 tour files under `static/tests/tours/` (web.assets_tests) is deleted or renamed
        without updating the module's own glob contribution - a literal missing path resolves to
        `AssetNotFound("Could not find %s" % name)` from `WebAsset.stat()`'s failed ir.attachment
        fallback (assetsbundle.py:744-751), re-raised as `AssetError('Could not get content for
        %s.' % name)` by `_fetch_content()`'s catch-all (:787-788, since AssetNotFound is not an
        IOError), then swallowed into an embedded `console.error("'Could not get content for
        viin_backend_theme/...' in file 'viin_backend_theme/...'")` string
        (assetsbundle.py:726-728+806-808) rather than raised - which is why this test
        regex-matches the compiled output for `in file '<this module's own path>'` (the one thing
        every such failure message is always wrapped in) instead of merely checking the build did
        not raise; OR a genuine JS syntax fault in one of those files, which DOES raise uncaught
        from the ES-module transpile step (assetsbundle.py:822) when the bundle is built.

        The match is deliberately scoped to `in file '<viin_backend_theme/...>'` (see the
        module-level `_MISSING_OWN_ASSET_RE` docstring) rather than any bare English phrase: both
        bundles also carry core's OWN files (e.g.
        base/static/tests/test_ir_model_fields_translation.js), whose ordinary test content can
        legitimately contain a phrase like "does not exist" unrelated to any missing asset - a
        bare-substring check false-reds on those every time, and the realistic missing-file
        message for this module's own bare-append entries does not even say "does not exist" (see
        above) - only the `generate_error` wrapping is guaranteed present regardless of wording.
        """
        for bundle_name in JS_BUNDLES:
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=False, js=True)
                js_attachment = bundle.js()
                self.assertTrue(
                    js_attachment,
                    "%s did not produce a JS attachment - the bundle did not build." % bundle_name,
                )
                js = (js_attachment.raw or b"").decode("utf-8", "replace")
                match = _MISSING_OWN_ASSET_RE.search(js)
                self.assertIsNone(
                    match,
                    "%s compiled with a swallowed missing-asset error for one of this module's "
                    "own files (matched %r) - that file no longer exists on disk."
                    % (bundle_name, match.group(0) if match else None),
                )
