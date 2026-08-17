# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Live-instance positive-evidence oracle for the SaverScreen branding fix.

Runs ``ViinBrandPosSaverScreenLogoTour`` (static/tests/tours/
saver_screen_logo_tour.js), which navigates to point_of_sale.SaverScreen and
asserts the RESOLVED ``background-image`` of its ``.pos-logo`` element names
the Viindoo asset - not merely that the screen renders without throwing.

RED today (before the production fix): the dead xpath in
static/src/app/screens/saver_screen.xml raises an OwlError the first time
SaverScreen is rendered, destroying the whole POS root component - the
``.login-overlay .pos-logo`` trigger the tour waits for never appears, so
this test fails by timeout rather than by a wrong assertion. That is the
correct RED: it fails for the actual production defect (an OwlError that
crashes a live POS session after 5 idle minutes), not a narrower proxy of
it.
"""
from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class TestViinBrandPosSaverScreenLogo(TestPointOfSaleHttpCommon):
    def test_saver_screen_shows_the_viindoo_logo(self):
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour("ViinBrandPosSaverScreenLogoTour")
