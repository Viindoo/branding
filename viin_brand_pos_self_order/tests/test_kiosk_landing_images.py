import hashlib

from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools import convert_file, file_open

IMAGE_NAMES = ('landing_01.jpg', 'landing_02.jpg', 'landing_03.jpg')
CORE_URL = '/pos_self_order/static/img/%s'
OWN_URL = '/viin_brand_pos_self_order/static/img/%s'


@tagged('post_install', '-at_install')
class TestKioskLandingImages(TransactionCase):

    def _landing_urls(self, config):
        return sorted(config.self_ordering_image_home_ids.mapped('url'))

    def test_kiosk_created_after_the_install_shows_the_images_of_viindoo(self):
        config = self.env['pos.config'].create({'name': 'Kiosk created after', 'self_ordering_mode': 'kiosk'})
        self.assertEqual(self._landing_urls(config), [OWN_URL % name for name in IMAGE_NAMES])

    def test_kiosk_switched_on_without_images_shows_the_images_of_viindoo(self):
        config = self.env['pos.config'].create({'name': 'Kiosk switched on'})
        config.write({'self_ordering_mode': 'kiosk'})
        self.assertEqual(self._landing_urls(config), [OWN_URL % name for name in IMAGE_NAMES])

    def test_kiosk_whose_images_are_cleared_gets_the_images_of_viindoo_back(self):
        config = self.env['pos.config'].create({'name': 'Kiosk cleared', 'self_ordering_mode': 'kiosk'})
        config.write({'self_ordering_image_home_ids': [(5, 0, 0)]})
        config.write({'self_ordering_mode': 'kiosk', 'self_ordering_image_home_ids': []})
        self.assertEqual(self._landing_urls(config), [OWN_URL % name for name in IMAGE_NAMES])

    def test_kiosk_created_before_the_install_is_pointed_at_the_images_of_viindoo(self):
        config = self.env['pos.config'].create({'name': 'Kiosk created before', 'self_ordering_mode': 'kiosk'})
        core_images = self.env['ir.attachment'].create([{
            'name': name,
            'type': 'url',
            'url': CORE_URL % name,
            'res_model': 'pos.config',
        } for name in IMAGE_NAMES])
        config.self_ordering_image_home_ids = core_images
        self.assertEqual(self._landing_urls(config), [CORE_URL % name for name in IMAGE_NAMES])

        self.env['pos.config']._use_brand_landing_images()

        self.assertEqual(self._landing_urls(config), [OWN_URL % name for name in IMAGE_NAMES])
        self.assertEqual(config.self_ordering_image_home_ids, core_images, 'the attachments are kept')

    def test_installing_the_module_points_the_kiosks_created_before_at_the_images_of_viindoo(self):
        config = self.env['pos.config'].create({'name': 'Kiosk created before', 'self_ordering_mode': 'kiosk'})
        config.self_ordering_image_home_ids = self.env['ir.attachment'].create([{
            'name': name,
            'type': 'url',
            'url': CORE_URL % name,
            'res_model': 'pos.config',
        } for name in IMAGE_NAMES])

        convert_file(self.env, 'viin_brand_pos_self_order', 'data/pos_config_data.xml', {}, 'init', False)

        self.assertEqual(self._landing_urls(config), [OWN_URL % name for name in IMAGE_NAMES])

    def test_image_a_user_chose_is_left_alone(self):
        own_image = self.env['ir.attachment'].create({
            'name': 'shop.jpg',
            'type': 'url',
            'url': 'https://example.com/shop.jpg',
            'res_model': 'pos.config',
        })
        config = self.env['pos.config'].create({
            'name': 'Kiosk with its own image',
            'self_ordering_mode': 'kiosk',
            'self_ordering_image_home_ids': [(6, 0, own_image.ids)],
        })

        self.env['pos.config']._use_brand_landing_images()

        self.assertEqual(self._landing_urls(config), ['https://example.com/shop.jpg'])


@tagged('post_install', '-at_install')
class TestKioskLandingImageFiles(HttpCase):

    def test_images_of_viindoo_are_served_and_differ_from_the_core_images(self):
        for name in IMAGE_NAMES:
            with self.subTest(image=name):
                response = self.url_open(OWN_URL % name)
                self.assertEqual(response.status_code, 200)
                with file_open('pos_self_order/static/img/%s' % name, 'rb') as core_image:
                    self.assertNotEqual(
                        hashlib.sha256(response.content).digest(), hashlib.sha256(core_image.read()).digest())
