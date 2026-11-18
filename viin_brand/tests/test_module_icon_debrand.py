import os

from odoo.modules import module as odoo_module
from odoo.modules.module import Manifest, get_module_path
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestModuleIconDebrand(TransactionCase):
    """Pins the module-icon de-brand with hard-coded Viindoo paths.

    viin_brand remaps every module's icon to the Viindoo icon set via
    ``get_viin_brand_module_icon``, wired onto ``odoo.modules.module.get_module_icon``
    in ``post_load``. The expected values here are fixed literals: building them
    from ``get_viin_brand_module_icon`` / ``check_viin_brand_module_icon`` would only
    compare the resolver with itself.

    Skipped when the branding module is not resolvable, not installable or its icon
    assets are absent, matching ``check_viin_brand_module_icon``'s own precondition.
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
        """Resolve through the viin_brand-patched ``get_module_icon`` global.

        Accessed at call time, not via a top-level ``from ... import``, so the patched
        function is observed rather than a pre-patch binding.
        """
        return odoo_module.get_module_icon(module_name)

    def test_app_module_icons_are_viindoo_branded(self):
        """Modules that ship a dedicated Viindoo app icon must resolve to it.

        Fixed literals: a de-brand that reverts to the stock Odoo
        ``/<module>/static/description/icon.png`` fails these assertions.
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

        A module whose stock icon is ``/base/static/description/icon.png`` must map to
        the branded base icon.
        """
        probe = "no_such_module_for_icon_test"
        # The probe ships no app icon of its own, so a branded result can only come
        # from the base fallback.
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
