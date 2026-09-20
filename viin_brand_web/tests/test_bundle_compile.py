# Bundle-compile requirement - protects the business rule: "every asset anchor and SCSS/JS
# contribution this module makes to a bundle resolves and compiles cleanly." Odoo validates
# NEITHER at install time, verified against odoo/addons/base/models/:
#   * a ('before'/'after'/'replace', anchor, source) directive resolves its ANCHOR through
#     AssetPaths.index() (ir_asset.py:396), called from _process_path (ir_asset.py:229) on every
#     _get_asset_paths() run (ir_asset.py:129) - a renamed/removed anchor makes it raise
#     ValueError("File(s) ... not found in bundle ...") (ir_asset.py:431, _raise_not_found). This
#     only happens when a bundle is actually RESOLVED - no `ir_asset` symbol is referenced anywhere
#     in odoo/modules/loading.py or odoo/modules/registry.py, so -i/-u never triggers it;
#   * a CONTRIBUTED file that is missing or malformed surfaces only when its own content is
#     fetched: WebAsset._fetch_content (assetsbundle.py:774-788) raises some AssetError subclass -
#     for a bare-append entry whose file is simply gone, that is the bare `except:` re-wrap
#     (`AssetError('Could not get content for %s.' % self.name)`), not the rarer IOError-on-a-
#     resolved-filename branch - which StylesheetAsset._fetch_content (assetsbundle.py:935-958)
#     catches (by the shared `AssetError` base, regardless of which subclass/message) and appends
#     to `bundle.css_errors` instead of raising; a genuine Sass fault (undefined variable/function,
#     bad map-merge) lands in that same list;
#   * for a JS asset the same failure is instead SWALLOWED into an embedded `console.error(...)`
#     string (JavascriptAsset.generate_error, assetsbundle.py:806-808) rather than raised or
#     recorded in any list - so a bare `bundle.js()` call that merely "does not raise" is a vacuous
#     check for a missing JS file; a real JS syntax fault still raises uncaught, from the ES-module
#     transpile step (JavascriptAsset.content, assetsbundle.py:822).
# A module with a dangling anchor or a broken SCSS/JS contribution therefore installs clean and
# only explodes - or silently degrades - the first time a browser actually asks for the bundle.
# This file is that compile, for every bundle in this module's __manifest__.py `assets` key that is
# not already guarded elsewhere.
#
# web.assets_backend already carries this exact guard - see
# tests/test_brand_cascade_compile.py::test_backend_bundle_compiles_without_css_errors - and is
# deliberately NOT duplicated here (one fact, one place).
#
# web._assets_primary_variables is deliberately NOT compiled standalone. It is a PRIVATE
# (leading-underscore) helper bundle that core never serves on its own: web/__manifest__.py
# declares it as only `primary_variables.scss` + `**/*.variables.scss` (where this module's
# anchored brand_variables.scss lands), while the Sass FUNCTIONS that file calls (e.g.
# `o-to-rem()`) live in the sibling `web._assets_helpers` bundle, which `_assets_primary_variables`
# never includes. Resolving it in isolation would report an "undefined function" Sass error
# UNCONDITIONALLY - a defect of the probe, not of this module - so it would be a broken
# measurement, not a guard. Its anchor is exercised for real every time `web.assets_web_dark` or
# `web.assets_backend_lazy_dark` (both guarded below) compiles, since each pulls it in
# transitively through `web._assets_helpers`.
import re

from odoo.tests.common import TransactionCase, tagged

# Top-level bundles this module contributes SCSS to that carry no compile guard elsewhere. Each is
# a real, independently-served bundle (never a private helper), so a non-empty compiled payload is
# both safe to assert and the observable this guard exists to protect.
CSS_BUNDLES = (
    "web.assets_web_dark",
    "web.assets_backend_lazy_dark",
)

# Bundles this module contributes only JS/tour files to (web.assets_unit_tests,
# web.assets_tests) - see the module docstring for why a JS bundle needs its own, stricter check.
JS_BUNDLES = (
    "web.assets_unit_tests",
    "web.assets_tests",
)

# For a bare-string entry (every one of this module's own manifest entries) whose file is simply
# absent, ir.asset._get_paths (ir_asset.py:317-375) never resolves a real filename - it falls
# through to its own "False path" branch (`paths = [(path_def, None, None)]`), so WebAsset._filename
# stays None. WebAsset.stat() (assetsbundle.py:744-751) then tries the ir.attachment fallback,
# which also misses, and raises `AssetNotFound("Could not find %s" % self.name)`; back in
# _fetch_content (:774-788) that is NOT an IOError, so the `except IOError: ... "File %s does not
# exist."` branch (:786) does NOT fire (that one is for a rarer on-disk race, not "the manifest
# lists a file that is gone") - it falls to the bare `except:` and is re-wrapped as
# `AssetError('Could not get content for %s.' % self.name)`. The exact wording therefore varies by
# failure shape (`AssetNotFound`/`AssetError`, several possible messages), so grepping for one
# specific phrase like "does not exist" is not just uncollision-proof against core noise (confirmed
# by an actual integrated run false-failing on base/static/tests/test_ir_model_fields_translation.js
# for exactly that reason) - it can also miss THIS module's own realistic failure entirely, since
# that case does not produce "does not exist" at all.
#
# What every one of those failure shapes DOES share: WebAsset.generate_error (assetsbundle.py:
# 726-728) wraps whichever message fired as `f'{msg!r} in file {self.url!r}'` before
# JavascriptAsset.generate_error (:806-808) embeds it in a console.error(...) call - so the
# substring `in file 'viin_brand_web/<path>'` is guaranteed present for THIS module's own asset
# regardless of which AssetError subclass or message text fired, and is scoped to this module's own
# path prefix (no other module's asset resolves to a url starting with `viin_brand_web/`).
_MISSING_OWN_ASSET_RE = re.compile(r"in file 'viin_brand_web/[\w./-]{0,200}'")


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every asset bundle this module contributes to must actually resolve and compile clean."""

    def test_css_bundles_compile_without_errors(self):
        """web.assets_web_dark / assets_backend_lazy_dark compile with real CSS.

        WOULD FAIL IF: the ('before', 'web/static/src/scss/primary_variables.scss', ...) /
        ('after', 'web/static/src/scss/primary_variables.scss', ...) anchors this module declares
        for these two bundles are renamed or removed by a future core upgrade (raises ValueError
        before this test's own assertions run - see the module docstring), or a Sass fault in ANY
        file this module's __manifest__.py lists under either bundle key populates
        bundle.css_errors. Deliberately NOT a fixed file enumeration (see
        test_brand_cascade_compile.py::test_backend_bundle_compiles_without_css_errors for the same
        choice on web.assets_backend): this cluster's module-independence relocation work keeps
        adding/removing dark-arm entries unit by unit, and a named list here goes stale exactly as
        often (confirmed: notebook.dark.scss, relocated here before this docstring was last
        touched, was already missing from the prior enumeration) - `__manifest__.py`'s own
        per-bundle file list, not this docstring, is the one place that must stay current.

        Both `css_errors` and the payload markers are checked - the same two-halves idiom this
        cluster already uses in test_brand_cascade_compile.py::test_backend_bundle_compiles_without_css_errors
        and test_mail_contrast_compile.py::test_module_scss_compiles_without_errors_in_every_bundle_it_is_served_in
        - because `.css()` returns early on an already-cached attachment WITHOUT repopulating
        `css_errors`, so a bundle that failed on an EARLIER compile would otherwise read green here
        while still serving the fallback stylesheet (assetsbundle.py:496-511, the literal
        "## CSS error message ##" / "css_error_message" / "A css error occured" markers it bakes
        into that payload).
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
        """web.assets_unit_tests / assets_tests resolve every listed file and build clean JS.

        WOULD FAIL IF: any of the bare-string .test.js / tour .js entries this module lists for
        these two bundles is deleted or renamed without updating __manifest__.py - the missing
        file is swallowed into an embedded `console.error("'...' in file
        'viin_brand_web/...'")` string (assetsbundle.py:726-728+806-808) rather than raised, which
        is why this test greps the compiled output for that module-scoped `in file '...'` marker
        instead of merely checking the build did not raise (see the module docstring above
        _MISSING_OWN_ASSET_RE for why the exact failure-message wording is not safe to grep for,
        but the `in file` wrapper always is); OR a genuine JS syntax fault in one of those files,
        which DOES raise uncaught from the ES-module transpile step (assetsbundle.py:822) when the
        bundle is built.
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
                    "%s compiled with a swallowed missing-asset error embedded as a console.error "
                    "call (%r) - one of this module's own listed files in this bundle no longer "
                    "exists on disk." % (bundle_name, match.group(0) if match else None),
                )
