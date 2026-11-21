# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo.tests.common import new_test_user, tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase

STOCK_TERM = '<b>Technical Rooms</b> - One dedicated to advanced Odoo developers, one for new developers.'


@tagged('post_install', '-at_install')
class TestEventDescriptionTranslation(NoupdateTranslationCase):

    def _hold_stock_description(self):
        """Return the main company's sample event, still in its stock Vietnamese."""
        event = self.env['event.event'].create({
            'name': 'Design Fair',
            'date_begin': datetime(2030, 1, 1, 9),
            'date_end': datetime(2030, 1, 3, 18),
            'company_id': self.env.ref('base.main_company').id,
            'description': '<p>%s</p>' % STOCK_TERM,
        })
        self.env['ir.model.data'].create({
            'module': 'event', 'name': 'event_0', 'model': 'event.event',
            'res_id': event.id, 'noupdate': True,
        })
        self.load_stock_then_branding_catalog(['event'], 'viin_brand_website_event')
        event.with_context(lang='vi_VN').description = '<p>%s</p>' % STOCK_TERM
        event.description = '<p>%s</p>' % STOCK_TERM.replace('Odoo', 'Viindoo')
        self.assertHoldsStockWording(self.translated(event, 'description'))
        return event

    def test_event_description_of_a_language_loaded_before_the_module_names_viindoo(self):
        event = self._hold_stock_description()
        self.load_catalog('viin_brand_website_event')
        self.assertNamesNoOdoo(self.translated(event, 'description'))

    def test_language_installed_by_another_company_admin_names_viindoo(self):
        """The Languages wizard runs as its user, who cannot see this event."""
        event = self._hold_stock_description()
        other_company = self.env['res.company'].create({'name': 'Second Company'})
        administrator = new_test_user(
            self.env, login='second_company_admin', groups='base.group_system',
            company_id=other_company.id, company_ids=[(6, 0, other_company.ids)],
        )
        self.assertFalse(event.with_user(administrator).has_access('read'))
        wizard = self.env['base.language.install'].with_user(administrator).create({
            'lang_ids': [(6, 0, self.env.ref('base.lang_vi_VN').ids)],
        })
        wizard.lang_install()
        self.assertNamesNoOdoo(self.translated(event, 'description'))
