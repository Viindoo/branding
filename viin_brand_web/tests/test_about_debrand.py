# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestAboutDebrand(HttpCase):
    """Protect the web-client de-brand of the General Settings 'About' block.

    The core `res_config_edition` view-widget renders the Odoo version heading and the
    'Odoo S.A.' copyright inside <div id="about"> on General Settings. viin_brand_web
    overrides that QWeb template to show the Viindoo brand instead. This drives the real
    Settings page in a headless browser and asserts (via the tour) that the rendered About
    block shows 'Viindoo' and no longer shows the stock 'Odoo' / 'Odoo S.A.' brand strings.
    """

    def test_about_section_shows_viindoo_brand_not_odoo(self):
        # Runs the viin_brand_web_about_debrand tour against General Settings as admin.
        # Tour completion == every assertion (branded present, Odoo absent) held; a missing
        # or broken override makes the negative-assertion steps time out and this test fail.
        self.start_tour(
            '/odoo/settings',
            'viin_brand_web_about_debrand',
            login='admin',
        )
