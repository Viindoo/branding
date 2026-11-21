# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestEventStageTranslation(NoupdateTranslationCase):

    def test_done_stage_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['event'], 'viin_brand_event')
        stage = self.env.ref('event.event_stage_done')
        self.assertHoldsStockWording(self.translated(stage, 'description'))
        self.load_catalog('viin_brand_event')
        self.assertNamesNoOdoo(self.translated(stage, 'description'))
