# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.brand_gradient import BrandGradientCase


@tagged("post_install", "-at_install")
class TestSponsorGradient(BrandGradientCase):

    def test_sponsor_card_gradient_is_the_content_purple(self):
        """The banner of a sponsor card is painted with core's gradient (same angle, second stop
        10% darker) in the Viindoo content purple instead of the Odoo purple.

        WOULD FAIL IF REVERTED: without the stylesheet of this module the gradient keeps the
        Odoo purple literal of core; a gradient of another shape or colour changes a stop."""
        self.assertBrandGradient({"o_wesponsor_gradient", "card-img-top"}, {"o_wesponsor_index"})
