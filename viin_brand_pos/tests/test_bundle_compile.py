# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Every asset bundle this module contributes to must actually compile clean.

Odoo validates an asset bundle's contents LAZILY - the first time a browser (or this test) asks
for it to be built - never at module install:

* An ``('after'/'before'/'replace', anchor, source)`` directive resolves its ANCHOR through
  ``AssetPaths.index()`` (``odoo/addons/base/models/ir_asset.py:396``), called from
  ``_process_path`` (``ir_asset.py:229``) every time ``_get_asset_paths()`` runs. A renamed or
  removed anchor makes it raise ``ValueError("File(s) %s not found in bundle %s")``
  (``ir_asset.py:431-432``, ``_raise_not_found``) - BEFORE any css()/js() split even happens,
  since ``ir_qweb._get_asset_bundle()`` resolves the full path list first
  (``ir_qweb.py:2829-2851``, ``_get_asset_content`` -> ``_get_asset_paths``). No ``ir_asset``
  symbol is referenced anywhere in ``odoo/modules/loading.py`` or ``odoo/modules/registry.py``, so
  ``-i``/``-u`` never triggers this at all - a module with a dangling anchor installs clean and
  only explodes the first time a browser actually asks for the bundle.
* A CONTRIBUTED file that is missing or malformed surfaces only when its own content is fetched.
  For a literal (non-glob) path, a missing file still produces one path entry with no real
  filename (``ir_asset.py``'s ``_get_paths``, the "attachment url most likely" branch), so
  ``WebAsset._fetch_content`` (``assetsbundle.py:774-786``) ends up raising ``AssetNotFound``
  ("Could not find %s" from ``stat()`` at :750, re-wrapped as "Could not get content for %s" by
  the bare ``except:`` at :786, or "File %s does not exist." at :785 for a same-request race). A
  ``StylesheetAsset`` (.css/.scss/.sass/.less) CATCHES that and appends it to ``bundle.css_errors``
  (:958); a ``JavascriptAsset`` (.js) SWALLOWS it into an embedded ``console.error(...)`` string
  (:806-808, :834-838) rather than raising; an ``XMLAsset`` (.xml template) instead RAISES
  ``XMLAssetError`` (:881-882), which propagates out of ``xml()`` (uncaught there - it only catches
  ``etree.ParseError``, :447-448) and is caught one level up by ``generate_xml_bundle()`` and
  embedded as a literal ``throw new Error(...)`` statement in the compiled JS text (:390-392). A
  GLOB entry (``**/*``), by contrast, just silently drops a deleted file from the resolved list -
  no error at all (``ir_asset.py``'s ``_get_paths``, wildcard branch) - which is the one hazard
  class this compile CANNOT catch; noted per-bundle below where it applies. A genuine Sass fault
  (undefined variable/function) in a contributed .scss file populates ``bundle.css_errors`` via
  ``compile_css`` (:614-616); a genuine JS syntax fault raises uncaught from the ES-module
  transpile step (``JavascriptAsset.content``, :822-824) - .css files are never Sass-compiled at
  all (only ``Sass``/``Scss``/``Less`` StylesheetAsset subclasses reach the compiler,
  :577-579), so a plain-CSS syntax typo is NOT caught here; also noted below.

This module contributes to four bundles (``__manifest__.py``'s ``assets`` key), verified against
that file directly rather than assumed:

* ``point_of_sale._assets_pos`` - two SCSS anchors (``pos_variables.scss`` after
  ``viin_brand_web``'s ``brand_variables.scss``; ``style.scss`` after ``point_of_sale``'s
  ``pos.scss``), four bare XML templates, ``navbar.js``, and one JS anchor
  (``offline_error_popup.js`` after ``point_of_sale``'s ``error_handlers.js``). Despite the
  leading underscore marking it "private" (never served on its own page), it is NOT a bare-helper
  bundle like ``web._assets_primary_variables`` (whose own Sass functions live in a SIBLING bundle
  it never includes, so resolving it in isolation raises an unconditional "undefined function"
  Sass error - a defect of the probe, not of whichever module contributes to it). Verified via
  ``point_of_sale/__manifest__.py``: ``_assets_pos`` opens with
  ``('include', 'point_of_sale.base_app')``, and ``base_app`` itself
  ``('include', 'web._assets_helpers')`` before anything else - and ``web._assets_helpers``
  (``web/__manifest__.py:376-391``) declares its own Sass functions/mixins FIRST, THEN
  ``('include', 'web._assets_primary_variables')`` (where ``viin_brand_web`` anchors
  ``brand_variables.scss`` 'before' ``primary_variables.scss``). So by the time this module's own
  two SCSS files are appended - viin_brand_pos being the most-dependent addon, processed last in
  the topological order - every Sass function/variable they could need is already resolved INSIDE
  this same bundle assembly. ``_assets_pos`` is therefore self-sufficient to compile alone; the
  private-helper failure mode that rules out ``_assets_primary_variables`` does not apply here.
* ``point_of_sale.assets_prod`` - the bundle Odoo actually serves at ``/pos/ui``
  (``point_of_sale/__manifest__.py``: "Bundle that starts the pos"), defined as
  ``('include', 'point_of_sale._assets_pos')`` + core's own ``main.js``. This module's own addition
  is a GLOB append with no anchor (``viin_brand_pos/static/src/css/**/*``, currently matching one
  plain ``.css`` file, not ``.scss``). Because it includes ``_assets_pos``, it is capable of
  failing for every reason above's ``_assets_pos`` case is - genuinely redundant with that check,
  kept anyway because it is the bundle actually served, not the private one. Its own addition,
  being a glob with no anchor and a plain (non-Sass) extension, has a narrower guarantee: this test
  catches a decode/fetch fault in that file (:958) but NOT a silent rename/deletion (glob just
  drops it) NOR a plain-CSS syntax typo (no Sass validation applies to ``.css``) - stated plainly
  rather than papered over.
* ``web.assets_tests`` - one GLOB append, no anchor (``static/tests/tours/**/*``, currently
  ``saver_screen_logo_tour.js``). Same glob caveat as above: a rename/deletion is a silent drop,
  not caught here. What IS caught: a genuine JS syntax fault in that tour file breaking the ES
  transpile step for the WHOLE bundle - a real, everyday hazard, since this bundle is shared by
  every module's tours in the same database.
* ``web.assets_unit_tests`` - two LITERAL (non-glob) appends: ``navbar.js`` (redundant re-declare
  of the same file already in ``_assets_pos`` - the manifest's own comment calls this "harmless
  redundancy") and ``navbar_favicon_guard.test.js`` (this module's own Hoot unit test). Being
  literal paths, NOT globs, a deletion of either DOES produce the missing-content marker (the
  glob-silent-drop caveat above does not apply to this bundle).
"""
import re

from odoo.tests.common import TransactionCase, tagged

# Bundles this module contributes SCSS/CSS to. point_of_sale._assets_pos carries this module's two
# real ('after', anchor, source) SCSS directives directly; .assets_prod inherits that same anchor
# coverage transitively (it 'include's _assets_pos) and additionally carries this module's own
# glob-appended plain CSS file - see the module docstring for the exact per-bundle breakdown.
CSS_BUNDLES = (
    "point_of_sale._assets_pos",
    "point_of_sale.assets_prod",
)

# Bundles this module contributes JS/XML-template files to. point_of_sale._assets_pos again,
# because it is a mixed bundle: its SCSS half is asserted above, its JS/XML half here.
JS_BUNDLES = (
    "point_of_sale._assets_pos",
    "web.assets_tests",
    "web.assets_unit_tests",
)

# JavascriptAsset.generate_error wraps a missing-JS-asset AssetError as `console.error("...");`
# (assetsbundle.py:806-808); generate_xml_bundle() catches a missing/malformed XML template's
# XMLAssetError and embeds `throw new Error("...");` (assetsbundle.py:390-392). Both wrap a
# json.dumps(...) string - always double-quoted, any internal quote backslash-escaped, never
# containing a literal unescaped '"' - so this non-greedy pattern captures one whole call intact.
_SWALLOWED_ASSET_ERROR_CALL_RE = re.compile(
    r'(?:console\.error|throw new Error)\("(?:[^"\\]|\\.)*"\)'
)

# A compiled bundle carries core's/point_of_sale's own source verbatim, and legitimate core code
# freely uses both console.error(...) and throw new Error(...) with its own arbitrary messages -
# so a bare phrase-anywhere-in-bundle scan for wording like "does not exist" false-reds on that
# unrelated content (a module's boot-time module-loader error, an unrelated test helper's own
# thrown Error, etc. - none of it a missing viin_brand_pos asset). What is actually diagnostic:
# WebAsset.generate_error (assetsbundle.py:726-728, `f'{msg!r} in file {self.url!r}'`) always
# bakes the FAILING asset's OWN url into the wrapped message - so a call that is genuinely about
# one of this module's own listed files always names this module's own path INSIDE that same
# call. A random core file's legitimate console.error/throw text never happens to also contain
# this module's technical name.
_OWN_ASSET_PATH_PREFIX = "viin_brand_pos/"


def _own_swallowed_asset_errors(js_text):
    """Return every swallowed-error call in ``js_text`` naming one of this module's own paths."""
    return [
        call for call in _SWALLOWED_ASSET_ERROR_CALL_RE.findall(js_text)
        if _OWN_ASSET_PATH_PREFIX in call
    ]


# The three literal fallback markers AssetsBundle.preprocess_css bakes into a CACHED "css error"
# stylesheet (assetsbundle.py:496-511) when serving a bundle whose LAST compile failed - `.css()`
# returns that cached attachment WITHOUT repopulating css_errors, so checking css_errors alone
# would read green on a stale failure.
_CACHED_CSS_ERROR_MARKERS = ("## CSS error message ##", "css_error_message", "A css error occured")


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every bundle this module contributes to must actually resolve and compile clean."""

    def test_css_bundles_compile_without_errors(self):
        """point_of_sale._assets_pos / .assets_prod compile with real, error-free CSS.

        WOULD FAIL IF: either 'after' SCSS anchor this module declares in
        point_of_sale._assets_pos (viin_brand_web's brand_variables.scss, point_of_sale's
        pos.scss) is renamed or removed by a future upgrade - _get_asset_bundle() raises
        ValueError before this method's own assertions even run, so the test ERRORS - or a Sass
        fault in pos_variables.scss / style.scss populates bundle.css_errors.
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
                    "%s reported SCSS/CSS compile errors: %s" % (bundle_name, "; ".join(bundle.css_errors)),
                )
                self.assertTrue(
                    css.strip(),
                    "%s compiled to empty CSS - the bundle did not build." % bundle_name,
                )
                for marker in _CACHED_CSS_ERROR_MARKERS:
                    self.assertNotIn(
                        marker, css,
                        "%s served a CACHED CSS-error fallback payload (marker %r found) - an "
                        "earlier compile failed and this one only looked clean because css() "
                        "returned the cached attachment without repopulating css_errors."
                        % (bundle_name, marker),
                    )

    def test_js_bundles_build_with_no_missing_or_malformed_asset(self):
        """point_of_sale._assets_pos / web.assets_tests / web.assets_unit_tests build clean JS.

        WOULD FAIL IF: the 'after' JS anchor (offline_error_popup.js after point_of_sale's
        error_handlers.js) is renamed or removed - same uncaught ValueError as the CSS case,
        since anchor resolution happens before the css/js split - or navbar.js /
        navbar_favicon_guard.test.js (LITERAL, non-glob entries) is deleted, embedding a swallowed
        console.error that NAMES that path; or any of the four XML templates in
        point_of_sale._assets_pos is deleted or malformed, embedding a `throw new Error(...)` that
        likewise names that path; or a genuine JS syntax fault in any contributed file raises
        uncaught from the transpile step. (saver_screen_logo_tour.js is matched by a GLOB, not a
        literal entry - its own deletion silently drops it from the bundle rather than tripping
        either signal; see the module docstring's web.assets_tests note.) The missing-asset check
        is scoped to calls that name this module's own path (see _own_swallowed_asset_errors) -
        core/point_of_sale's own bundled source legitimately uses both console.error(...) and
        throw new Error(...) with unrelated wording of its own, so a bare phrase-anywhere scan
        would false-red on that content.
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
                own_errors = _own_swallowed_asset_errors(js)
                self.assertFalse(
                    own_errors,
                    "%s compiled with a swallowed error naming one of viin_brand_pos's own asset "
                    "paths (a missing JS file, or a missing/malformed XML template): %s"
                    % (bundle_name, own_errors),
                )
