import os

from odoo.modules import module as odoo_module
from odoo.modules.module import Manifest, get_module_path
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestModuleIconDebrand(TransactionCase):
    """Independent guard protecting the module-icon de-brand shipped by viin_brand.

    viin_brand UNCONDITIONALLY remaps every module's icon to the Viindoo icon set via
    ``get_viin_brand_module_icon``, wired onto ``odoo.modules.module.get_module_icon``
    in ``post_load``. The core mail Store tests we realign (see
    ``_patch_mailcommon_module_icon_expectation``) only prove that *expected*
    equals *actual* through our OWN resolver, so they cannot catch a regression in
    the resolver's VALUE - they would keep passing even if the de-brand produced a
    wrong (but self-consistent) icon.

    This case is the SSOT that pins the de-brand's real output with HARD-CODED
    Viindoo paths as the expected values. It deliberately NEVER calls
    ``get_viin_brand_module_icon`` / ``check_viin_brand_module_icon`` to build an
    expectation (that would be the same tautology) - the literals below are fixed.
    It mirrors ``viin_brand_mail``'s ``test_partner_root_debrand``, which guards
    that module's OdooBot -> ViindooBot de-brand with a fixed expectation.

    Skipped when the branding module is not resolvable / not installable / its icon
    assets are absent (e.g. viin_brand parked non-installable, or its icon assets stripped), matching
    ``check_viin_brand_module_icon``'s own precondition, so such runs do not
    false-fail. On the PR #658 runbot viin_brand is installable and present, so the
    guard runs and protects the behaviour.
    """

    def setUp(self):
        super().setUp()
        self.branding_path = get_module_path("viin_brand", display_warning=False)
        if not self.branding_path:
            self.skipTest("viin_brand is not in the addons path - de-brand inactive")
        manifest = Manifest.for_addon("viin_brand", display_warning=False)
        if not (manifest and manifest["installable"]):
            self.skipTest("viin_brand is not installable - de-brand inactive")
        if not os.path.exists(
            os.path.join(self.branding_path, "static", "img", "apps", "mail.png")
        ):
            self.skipTest("viin_brand app-icon assets are absent - de-brand inactive")

    def _module_icon(self, module_name):
        """Resolve through the LIVE, viin_brand-patched ``get_module_icon`` global.

        Accessed at call time (not via a top-level ``from ... import``) so we always
        observe the monkeypatched de-brand rather than a possibly pre-patch binding.
        """
        return odoo_module.get_module_icon(module_name)

    def test_app_module_icons_are_viindoo_branded(self):
        """Modules that ship a dedicated Viindoo app icon must resolve to it.

        Fixed literals - if the de-brand breaks (e.g. reverts to the stock Odoo
        ``/<module>/static/description/icon.png``) these assertions fail.
        """
        self.assertEqual(
            self._module_icon("mail"),
            "/viin_brand/static/img/apps/mail.png",
        )
        self.assertEqual(
            self._module_icon("crm"),
            "/viin_brand/static/img/apps/crm.png",
        )
        self.assertEqual(
            self._module_icon("im_livechat"),
            "/viin_brand/static/img/apps/im_livechat.png",
        )

    def test_base_fallback_icon_is_viindoo_branded(self):
        """A module with no icon of its own must resolve to the Viindoo BASE icon.

        This is the invariant behind ``base.IrModuleCase.test_missing_module_icon``
        (a module whose stock icon is ``/base/static/description/icon.png`` must map
        to the branded base icon), pinned here to the FIXED Viindoo base path so it
        fails if the de-brand's base-fallback branch breaks.
        """
        probe = "no_such_module_for_icon_test"
        # Precondition: the probe has NO dedicated Viindoo app icon of its own, so a
        # branded result can ONLY come from the base-fallback branch - not from a
        # module-specific asset. This keeps the assertion meaningful.
        self.assertFalse(
            os.path.exists(
                os.path.join(
                    self.branding_path, "static", "img", "apps", "%s.png" % probe
                )
            ),
            "probe module must not ship its own Viindoo app icon",
        )
        self.assertEqual(
            self._module_icon(probe),
            "/viin_brand/static/img/apps/base.png",
        )
