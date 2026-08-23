import logging

from odoo.tests.common import HttpCase, tagged

_logger = logging.getLogger(__name__)

MODULE = "viin_brand_common"


def _brand_core_path(relative):
    return "/%s/static/src/core/%s" % (MODULE, relative)


# The three "core patch" files carried ONLY by this module's web._assets_core
# glob (__manifest__.py 'web._assets_core':
#  [('after', 'web/static/src/core/**/*', 'viin_brand_common/static/src/core/**/*')]).
# Nothing else in this module's manifest declares any of these three anywhere
# but web.assets_backend, so their presence in ANY other bundle is
# unconditionally the leak this test exists to catch.
CORE_PATCH_FILES = (
    _brand_core_path("browser/title_service.js"),
    _brand_core_path("colors/colors.js"),
    _brand_core_path("file_viewer/file_viewer.scss"),
)

# emoji_picker.scss is DIFFERENT from the three above: __manifest__.py:148-153
# declares it into 'mail.assets_public' and 'im_livechat.assets_embed_core'
# EXPLICITLY and DELIBERATELY, independently of the glob:
#   'mail.assets_public': [
#       ('after', 'web/static/src/core/emoji_picker/emoji_picker.scss',
#        'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
#   ],
#   'im_livechat.assets_embed_core': [
#       ('after', 'web/static/src/core/emoji_picker/emoji_picker.scss',
#        'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
#   ],
# Removing the glob will not, and must not, remove emoji_picker.scss from the
# public mail page or the livechat embed - that sharing is intentional brand
# coverage, not a leak. Only its presence in a bundle with NO such explicit
# declaration (PoS, the attendance kiosk) is the bug.
EMOJI_PICKER_FILE = _brand_core_path("emoji_picker/emoji_picker.scss")

ALL_BRAND_ASSET_PATHS = CORE_PATCH_FILES + (EMOJI_PICKER_FILE,)

# web._assets_core is ('include', ...)-ed by FIVE bundles - verified by
# reading each owning manifest directly, never assumed from the bundle key
# alone:
#   web/__manifest__.py:54            -> web.assets_backend  (the ONLY
#                                         intended target - the real backend
#                                         webclient)
#   point_of_sale/__manifest__.py:114 -> point_of_sale.base_app
#                                         (the PoS terminal bundle - see the
#                                         "# PoS assets" comment a few lines
#                                         above its declaration)
#   mail/__manifest__.py:224          -> mail.assets_public
#                                         (the public, unauthenticated mail
#                                         page)
#   im_livechat/__manifest__.py:114   -> im_livechat.assets_embed_external,
#                                         NOT .assets_embed_core.
#                                         .assets_embed_core (declared at
#                                         im_livechat/__manifest__.py:87) has
#                                         its own ('remove',
#                                         'web/static/src/core/browser/title_service.js')
#                                         at line 88, which requires that file
#                                         to already be present - true only
#                                         when embed_core is composed INSIDE a
#                                         parent that already pulled in
#                                         web._assets_core. Resolved standalone
#                                         (as ir.asset._get_asset_paths() does
#                                         when given a bundle name directly) it
#                                         raises ValueError instead of
#                                         resolving. .assets_embed_external
#                                         (declared at line 100) is the bundle
#                                         that both ('include',
#                                         'web._assets_core')-s at line 114 AND
#                                         ('include',
#                                         'im_livechat.assets_embed_core')-s at
#                                         line 126, so it is the smallest
#                                         bundle that actually resolves and
#                                         carries the leak.
#                                         .assets_embed_cors further
#                                         ('include', ...)-s embed_external, so
#                                         checking embed_external covers that
#                                         whole family too.
#   hr_attendance/__manifest__.py:71  -> hr_attendance.assets_public_attendance
#                                         (the public kiosk app - see the
#                                         "# Public Kiosk app and its
#                                         components" comment a few lines
#                                         below its declaration)
# Every bundle below except web.assets_backend is owned by a module that
# installs strictly AFTER viin_brand_common (auto_install: ['web']), which is
# why this whole class must run post_install (see the class docstring).
NON_WEBCLIENT_BUNDLES = (
    ("point_of_sale.base_app", "point_of_sale"),
    ("mail.assets_public", "mail"),
    ("im_livechat.assets_embed_external", "im_livechat"),
    ("hr_attendance.assets_public_attendance", "hr_attendance"),
)

# The two non-webclient bundles this module's OWN manifest deliberately
# extends with emoji_picker.scss (__manifest__.py:148-153) - it belongs here
# too, on purpose, and must stay even after the glob is gone.
EMOJI_PICKER_INTENTIONAL_BUNDLES = (
    ("mail.assets_public", "mail"),
    ("im_livechat.assets_embed_external", "im_livechat"),
)

# NON_WEBCLIENT_BUNDLES minus the two above: bundles with NO explicit
# viin_brand_common declaration for emoji_picker.scss, so its presence there
# can only be the glob leak.
EMOJI_PICKER_UNDECLARED_BUNDLES = tuple(
    entry for entry in NON_WEBCLIENT_BUNDLES if entry not in EMOJI_PICKER_INTENTIONAL_BUNDLES
)

# The one bundle every brand asset belongs to - the counterweight side of the
# same contract.
WEBCLIENT_BUNDLE = "web.assets_backend"


@tagged("-at_install", "post_install")
class TestBrandAssetsOutOfPublicBundles(HttpCase):
    """Viindoo brand assets belong to the real backend webclient - plus, for
    ONE file, two bundles it was deliberately shared with - and to NOTHING
    ELSE: never a point-of-sale terminal, a public mail page (except that one
    deliberate share), an embedded livechat widget (same exception), or an
    employee attendance kiosk.

    This module's manifest currently ships a glob,
    ('after', 'web/static/src/core/**/*', 'viin_brand_common/static/src/core/**/*'),
    anchored on 'web._assets_core'. That bundle is ('include', ...)-d by FIVE
    bundles, not just the intended web.assets_backend, so the glob rides
    along on every one of them - pushing four brand files (2 JS, 2 SCSS) into
    a PoS terminal, the public mail page, the embedded livechat widget, and
    the attendance kiosk.

    The rule is NOT symmetric across those four files, and the test does not
    pretend it is:

    * CORE_PATCH_FILES (title_service.js, colors.js, file_viewer.scss) reach
      web.assets_backend and nowhere else - nothing in this module's manifest
      declares them anywhere else on purpose.
    * EMOJI_PICKER_FILE also reaches web.assets_backend, but ADDITIONALLY
      reaches mail.assets_public and im_livechat.assets_embed_external on
      purpose (__manifest__.py:148-153, independent of the glob). Only its
      presence in PoS or the attendance kiosk - which have no such
      declaration - is the bug.

    Encoding the wider "no brand asset anywhere but the webclient" rule
    would leave test_emoji_picker_is_absent_from_bundles_with_no_explicit_declaration
    permanently red even after the glob is correctly removed, which would
    either send the fix into a doomed loop or tempt someone into deleting an
    intentional declaration just to get green.

    Resolved via ir.asset._get_asset_paths() - Odoo's own bundle-composition
    resolver - rather than by fetching compiled CSS over HTTP the way
    tests/test_brand_css_out_of_test_bundles.py does for a different bundle
    set: two of the four leaked files are JS, which never appears in a
    compiled CSS response, so an HTTP/CSS-body approach would be structurally
    blind to half the leak.

    Every non-webclient bundle here is owned by a module (point_of_sale,
    mail, im_livechat, hr_attendance) that installs strictly AFTER
    viin_brand_common (auto_install: ['web']) - a default at_install class
    cannot see any of their manifests, so this class must run post_install.
    """

    def _asset_paths(self, bundle):
        """Return the set of web-relative paths ir.asset resolves for ``bundle``."""
        asset_paths = self.env["ir.asset"]._get_asset_paths(bundle, {})
        return {path for path, _full_path, _bundle, _modified in asset_paths}

    def _installed(self, module_names):
        return set(
            self.env["ir.module.module"]
            .search([("name", "in", list(module_names)), ("state", "=", "installed")])
            .mapped("name")
        )

    def _check_installed_bundles(self, bundles, assert_per_bundle, log_label, empty_message):
        """Run ``assert_per_bundle(paths, bundle, owning_module)`` for every
        bundle in ``bundles`` whose owning module is installed; skip the rest
        visibly. Fails loudly (never silently) if nothing could be checked.
        """
        installed = self._installed(owning_module for _bundle, owning_module in bundles)
        checked = []
        skipped = []
        for bundle, owning_module in bundles:
            if owning_module not in installed:
                skipped.append(bundle)
                continue
            checked.append(bundle)
            with self.subTest(bundle=bundle):
                assert_per_bundle(self._asset_paths(bundle), bundle, owning_module)
        _logger.info(
            "[brand-asset-guard] %s: checked=%s skipped=%s", log_label, checked, skipped
        )
        self.assertTrue(checked, empty_message)

    def test_core_patch_files_are_absent_from_non_webclient_bundles(self):
        """title_service.js / colors.js / file_viewer.scss may reach ONLY
        the real webclient. Unlike emoji_picker.scss, this module declares
        no explicit entry for any of these three anywhere else, so presence
        in a PoS terminal, the public mail page, the livechat embed, or the
        attendance kiosk is unconditionally the glob leak.
        """

        def assert_core_patch_absent(paths, bundle, owning_module):
            leaked = sorted(paths & set(CORE_PATCH_FILES))
            self.assertFalse(
                leaked,
                "%s (owned by %s, installed) still resolves %d core-patch "
                "brand asset(s) that must never reach it: %s. These are "
                "only supposed to reach %s."
                % (bundle, owning_module, len(leaked), ", ".join(leaked), WEBCLIENT_BUNDLE),
            )

        self._check_installed_bundles(
            NON_WEBCLIENT_BUNDLES,
            assert_core_patch_absent,
            "core-patch absence",
            "none of point_of_sale/mail/im_livechat/hr_attendance is "
            "installed on this database, so the core-patch leak check "
            "verified nothing. At least one must be installed for this "
            "guard to mean anything.",
        )

    def test_emoji_picker_is_absent_from_bundles_with_no_explicit_declaration(self):
        """emoji_picker.scss may reach mail.assets_public and
        im_livechat.assets_embed_external on purpose (see
        EMOJI_PICKER_INTENTIONAL_BUNDLES / the class docstring), but this
        module declares NO such entry for PoS or the attendance kiosk -
        presence there is still the same glob leak as the core-patch files.
        """

        def assert_emoji_picker_absent(paths, bundle, owning_module):
            self.assertNotIn(
                EMOJI_PICKER_FILE,
                paths,
                "%s (owned by %s, installed) resolves %s, but this "
                "module's manifest declares no explicit entry for it in "
                "%s - the only way it can have arrived is the leaking "
                "web._assets_core glob."
                % (bundle, owning_module, EMOJI_PICKER_FILE, bundle),
            )

        self._check_installed_bundles(
            EMOJI_PICKER_UNDECLARED_BUNDLES,
            assert_emoji_picker_absent,
            "emoji_picker undeclared-bundle absence",
            "neither point_of_sale nor hr_attendance is installed on this "
            "database, so the emoji_picker leak check verified nothing. At "
            "least one must be installed for this guard to mean anything.",
        )

    def test_emoji_picker_intentionally_still_reaches_mail_and_livechat_embed(self):
        """The asymmetry is deliberate (__manifest__.py:148-153): stripping
        the glob must NOT strip emoji_picker.scss from the two bundles it
        was explicitly, independently declared into. Without this positive
        check, a future "fix" that also deleted those two explicit entries -
        mistaking them for part of the leak - would go undetected: the
        absence checks above never look at these two bundles for this file.
        """

        def assert_emoji_picker_present(paths, bundle, owning_module):
            self.assertIn(
                EMOJI_PICKER_FILE,
                paths,
                "%s (owned by %s, installed) no longer resolves %s. "
                "__manifest__.py:148-153 declares this entry on purpose, "
                "independently of the web._assets_core glob - it must "
                "survive the glob's removal." % (bundle, owning_module, EMOJI_PICKER_FILE),
            )

        self._check_installed_bundles(
            EMOJI_PICKER_INTENTIONAL_BUNDLES,
            assert_emoji_picker_present,
            "emoji_picker intentional-presence",
            "neither mail nor im_livechat is installed on this database, "
            "so the intentional-sharing check verified nothing. At least "
            "one must be installed for this guard to mean anything.",
        )

    def test_all_brand_assets_still_reach_the_real_webclient(self):
        """Removing the leak must not remove the brand from the product itself.

        This is the assertion that stops the separation from being
        "achieved" by deleting the brand files outright: it fails the moment
        a fix drops one of them from web.assets_backend instead of only
        narrowing which OTHER bundles may still reach them.
        """
        paths = self._asset_paths(WEBCLIENT_BUNDLE)
        for asset_path in ALL_BRAND_ASSET_PATHS:
            with self.subTest(asset_path=asset_path):
                self.assertIn(
                    asset_path,
                    paths,
                    "%s no longer resolves %s. The real webclient must keep "
                    "every one of this module's core-bundle brand assets."
                    % (WEBCLIENT_BUNDLE, asset_path),
                )
