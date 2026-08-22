from odoo.tests.common import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestBrandAppearanceContract(HttpCase):
    """The Viindoo brand appearance, guarded on the REAL product.

    viin_brand_common now strips its own SCSS back out of
    ``web.assets_unit_tests_setup`` and ``web.tests_assets`` so core's Hoot and
    QUnit suites measure core's own design tokens instead of Viindoo's. That is
    the right fix, and it has a price: the unit-test page deliberately carries
    NO brand CSS any more, so brand-appearance regression lost the only place it
    used to be noticed. These tests are the replacement guard.

    They therefore have to run on the real webclient and the real website - a
    JS unit test could not detect any of this, because the page a JS unit test
    runs on is precisely the page the brand CSS was removed from.

    Every expected value lives in the tour file and comes from the Viindoo brand
    identity or from Odoo core's own published palette, never from reading the
    SCSS under guard.
    """

    # Pinned deliberately rather than inherited. HttpCase already defaults to
    # this size (odoo/tests/common.py:2173), but the campaign that produced
    # these tests lost a full measurement round to a browser window of
    # 1905x2053, where .o_content cannot scroll and unrelated tests fail for a
    # reason that has nothing to do with the code. Restating the size here
    # means a future change to core's default cannot silently move the ground
    # these assertions stand on. The tours print the viewport they actually ran
    # at next to every number they measure.
    browser_size = "1366x768"

    def _assert_website_is_installed(self):
        """Skip only where the contract genuinely does not exist.

        The website half of the palette contract needs a website to look at:
        without the ``website`` module, ``/`` is not a themed page at all, it is
        a redirect. viin_brand_common does not depend on ``website`` (it brands
        far more than the website), so the module can legitimately be installed
        without one.

        This is an environment guard, not a way to quieten a failing assertion:
        where ``website`` IS installed - the standard Viindoo stack, and the
        profile this guard was written for - the test runs and can fail.
        """
        installed = (
            self.env["ir.module.module"]
            .sudo()
            .search_count([("name", "=", "website"), ("state", "=", "installed")])
        )
        if not installed:
            self.skipTest(
                "the 'website' module is not installed, so '/' is a redirect "
                "rather than a themed page - the backend half of this contract "
                "is still covered by test_real_backend_paints_the_viindoo_brand_palette"
            )

    def test_real_backend_paints_the_viindoo_brand_palette(self):
        """The backend a user actually opens must paint the Viindoo cyan.

        Reads the background-color a browser really paints on the palette
        classes, not the text of a CSS variable: a variable can hold the right
        token while nothing consumes it.
        """
        self.start_tour("/odoo", "viin_brand_palette_tour", login="admin")

    def test_real_website_paints_the_same_palette_as_the_backend(self):
        """The website must serve the same palette as the backend.

        The website editor takes its theme colours from the page being edited,
        so a website whose palette has drifted from the backend's is a real
        product defect that no backend-only check would see. The two halves are
        asserted against the SAME brand constants rather than against each
        other on purpose - an equality check between the two pages would stay
        green if both drifted together.
        """
        self._assert_website_is_installed()
        self.start_tour("/", "viin_brand_website_palette_tour", login="admin")

    def test_real_backend_renders_text_at_the_brand_base_font_size(self):
        """Viindoo reads one step larger than core: 15px, not core's 14px."""
        self.start_tour("/odoo", "viin_brand_font_size_tour", login="admin")

    def test_real_backend_buttons_keep_the_brand_square_corners(self):
        """Square corners are part of the identity, not a Bootstrap default."""
        self.start_tour("/odoo", "viin_brand_square_corners_tour", login="admin")
