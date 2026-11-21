# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""The SaverScreen of the POS shows the Viindoo logo.

``ViinBrandPosSaverScreenLogoTour`` (static/tests/tours/saver_screen_logo_tour.js) opens the screen
and asserts that the resolved ``background-image`` of its ``.pos-logo`` element names the Viindoo
asset. A template extension that cannot be located destroys the whole POS root component, so the
tour also guards that the screen renders at all.
"""
from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class TestViinBrandPosSaverScreenLogo(TestPointOfSaleHttpCommon):
    def test_saver_screen_shows_the_viindoo_logo(self):
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour("ViinBrandPosSaverScreenLogoTour")
