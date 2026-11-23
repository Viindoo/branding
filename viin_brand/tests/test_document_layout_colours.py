# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import Form, TransactionCase, tagged

from odoo.addons.viin_brand import post_init_hook, _update_document_layout_colours
from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR, VIINDOO_THEME_COLOR

CHOSEN_PRIMARY = "#123456"
CHOSEN_SECONDARY = "#654321"


@tagged("post_install", "-at_install")
class TestDocumentLayoutColours(TransactionCase):
    """The colours of the layout of the documents of a company that never chose any are the colours
    of the brand: the deep teal of the frame as primary, the purple of the content as secondary."""

    def _company(self, **values):
        """Create a company, with a name of its own: the name of a company is unique."""
        name = "Layout colours company %d" % (self.env["res.company"].search_count([]) + 1)
        return self.env["res.company"].create(dict(name=name, **values))

    def test_a_new_company_gets_the_brand_colours(self):
        """A company created with no colour holds the teal and the purple, and a colour it is
        created with is kept.

        WOULD FAIL IF REVERTED: without the field defaults of viin_brand the colours stay empty and
        the wizard derives them from the logo, a mauve of the Odoo family."""
        company = self._company()
        self.assertEqual(company.primary_color, VIINDOO_THEME_COLOR)
        self.assertEqual(company.secondary_color, VIINDOO_BRAND_COLOR)
        chosen = self._company(primary_color=CHOSEN_PRIMARY, secondary_color=CHOSEN_SECONDARY)
        self.assertEqual((chosen.primary_color, chosen.secondary_color), (CHOSEN_PRIMARY, CHOSEN_SECONDARY))

    def test_the_install_hook_fills_only_the_companies_with_no_colour_at_all(self):
        """The hook gives the brand colours to a company whose two colours are both empty and leaves
        a company that holds one of them, or both, alone.

        WOULD FAIL IF REVERTED: a hook that fills every company, or every empty colour, overwrites
        or completes a choice of the company."""
        blank = self._company()
        blank.write({"primary_color": False, "secondary_color": False})
        both = self._company(primary_color=CHOSEN_PRIMARY, secondary_color=CHOSEN_SECONDARY)
        only_primary = self._company(primary_color=CHOSEN_PRIMARY)
        only_primary.secondary_color = False
        only_secondary = self._company(secondary_color=CHOSEN_SECONDARY)
        only_secondary.primary_color = False

        _update_document_layout_colours(self.env)

        self.assertEqual((blank.primary_color, blank.secondary_color), (VIINDOO_THEME_COLOR, VIINDOO_BRAND_COLOR))
        self.assertEqual((both.primary_color, both.secondary_color), (CHOSEN_PRIMARY, CHOSEN_SECONDARY))
        self.assertEqual((only_primary.primary_color, only_primary.secondary_color), (CHOSEN_PRIMARY, False))
        self.assertEqual((only_secondary.primary_color, only_secondary.secondary_color), (False, CHOSEN_SECONDARY))

    def test_the_module_install_hook_runs_the_colour_step(self):
        """The post-init hook of the module includes the colour step.

        WOULD FAIL IF REVERTED: dropping the call leaves the companies of an existing database with
        no colour."""
        company = self.env.company
        company.write({"primary_color": False, "secondary_color": False})
        post_init_hook(self.env)
        self.assertEqual((company.primary_color, company.secondary_color), (VIINDOO_THEME_COLOR, VIINDOO_BRAND_COLOR))

    def test_the_layout_wizard_of_a_company_with_no_chosen_colour_shows_the_brand_swatches(self):
        """The wizard "Configure your document layout" opens on the teal and the purple, and its
        report preview paints them.

        WOULD FAIL IF REVERTED: without the defaults the wizard derives the swatches from the logo
        and the preview carries that mauve."""
        company = self._company()
        company.logo = self.env.company.logo
        wizard = Form(self.env["base.document.layout"].with_company(company))
        self.assertEqual(wizard.company_id, company)
        self.assertEqual(wizard.primary_color, VIINDOO_THEME_COLOR)
        self.assertEqual(wizard.secondary_color, VIINDOO_BRAND_COLOR)
        preview = str(wizard.preview).lower()
        self.assertIn(VIINDOO_THEME_COLOR.lower(), preview)
        self.assertIn(VIINDOO_BRAND_COLOR.lower(), preview)
