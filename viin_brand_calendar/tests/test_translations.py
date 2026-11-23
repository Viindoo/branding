# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase

SYNC_SETTINGS = (
    'Synchronize your calendar with Google Calendar',
    'Synchronize your calendar with Outlook',
)


@tagged('post_install', '-at_install')
class TestCalendarSyncTranslation(NoupdateTranslationCase):

    def test_calendar_sync_settings_of_a_language_loaded_first_do_not_name_odoo(self):
        """The stock catalog names Odoo where the English does not; this one wins."""
        self.load_stock_catalogs(['calendar'])
        self.load_catalog('viin_brand_calendar')
        xmlid = 'calendar.res_config_settings_view_form'
        view = self.env.ref(xmlid)
        arch_vi = self.translated(view, 'arch_db')
        for source in SYNC_SETTINGS:
            with self.subTest(source=source):
                self.assertIn(source, view.with_context(lang='en_US').arch_db)
                stock_vi = self.catalog_translation('calendar', source, xmlid, core=True)
                self.assertNotIn(stock_vi, arch_vi)
                brand_vi = self.catalog_translation('viin_brand_calendar', source, xmlid)
                self.assertNotIn('Odoo', brand_vi)
                self.assertIn(brand_vi, arch_vi)
