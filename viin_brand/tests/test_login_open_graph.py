import os
import re
import struct
from urllib.parse import urlsplit

from odoo.tests.common import HttpCase, tagged
from odoo.tools import file_path

from odoo.addons.viin_brand.tools import VIINDOO_TWITTER_HANDLE

from .common import PRODUCT_NAME_IN_ENGLISH

ODOO_MARK_IN_META = re.compile(PRODUCT_NAME_IN_ENGLISH.pattern + r'|(?i:@odoo\b)')
OG_IMAGE_PATH = '/viin_brand/static/img/viindoo_og_image.png'
META_RE = re.compile(r'<meta\b[^>]*>', re.IGNORECASE)
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
CHECKED_META = (
    'og:site_name', 'twitter:site', 'og:title', 'twitter:title', 'og:description',
    'twitter:description', 'og:image:alt', 'twitter:image:alt',
)


def _png_size(path):
    with open(path, 'rb') as png:
        header = png.read(24)
    return struct.unpack('>II', header[16:24])


@tagged('post_install', '-at_install')
class TestLoginOpenGraph(HttpCase):
    """The preview of a shared /odoo link (Open Graph and Twitter card of the login page) names Viindoo."""

    def _metas(self):
        response = self.url_open('/web/login?redirect=/odoo')
        self.assertEqual(response.status_code, 200)
        metas = {}
        for tag in META_RE.findall(response.text):
            attributes = dict(ATTR_RE.findall(tag))
            key = attributes.get('property') or attributes.get('name')
            if key:
                metas[key] = attributes.get('content', '')
        return metas

    def test_preview_texts_carry_no_odoo_mark(self):
        metas = self._metas()

        for key in CHECKED_META:
            with self.subTest(meta=key):
                self.assertIn(key, metas)
                self.assertNotRegex(metas[key], ODOO_MARK_IN_META)
        self.assertEqual(metas['og:site_name'], 'Viindoo')
        self.assertEqual(metas['og:title'], 'Viindoo')

    def test_twitter_card_names_the_account_of_the_company_social_link(self):
        self.assertEqual(self._metas()['twitter:site'], VIINDOO_TWITTER_HANDLE)
        self.assertRegex(VIINDOO_TWITTER_HANDLE, r'^@\w+$')

    def test_preview_image_is_the_viindoo_one_with_its_real_size(self):
        metas = self._metas()

        for key in ('og:image', 'twitter:image'):
            self.assertEqual(urlsplit(metas[key]).path, OG_IMAGE_PATH)
        image = file_path('viin_brand/static/img/viindoo_og_image.png')
        width, height = _png_size(os.fspath(image))
        self.assertEqual((int(metas['og:image:width']), int(metas['og:image:height'])), (width, height))
