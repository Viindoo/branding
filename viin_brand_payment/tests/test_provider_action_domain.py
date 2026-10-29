from odoo.fields import Domain
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import convert_file
from odoo.tools.safe_eval import safe_eval


@tagged('post_install', '-at_install')
class TestProviderActionDomain(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Provider = cls.env['payment.provider']
        cls.action = cls.env.ref('payment.action_payment_provider')
        cls.enterprise_module = cls.env['ir.module.module'].create({
            'name': 'payment_enterprise_stub', 'to_buy': True, 'state': 'uninstallable',
        })
        cls.enterprise_provider = cls.Provider.create({
            'name': 'Enterprise provider',
            'code': 'none',
            'module_id': cls.enterprise_module.id,
        })
        cls.community_provider = cls.Provider.create({
            'name': 'Community provider',
            'code': 'none',
            'module_id': cls.env['ir.module.module'].search([('name', '=', 'payment')]).id,
        })

    def _listed(self):
        domain = Domain(safe_eval(self.action.domain or '[]'))
        providers = self.enterprise_provider | self.community_provider
        return self.Provider.search(domain & Domain('id', 'in', providers.ids))

    def test_enterprise_providers_are_hidden_from_the_providers_action(self):
        self.action.domain = False

        for _loaded_twice in range(2):
            convert_file(self.env, 'viin_brand_payment', 'data/payment_provider_data.xml', None)

        self.assertEqual(self._listed(), self.community_provider)
        self.assertEqual(self.action.domain.count('module_to_buy'), 1)

    def test_restoring_the_action_drops_only_the_to_buy_condition(self):
        self.action.domain = "[('company_id', '!=', False)]"
        convert_file(self.env, 'viin_brand_payment', 'data/payment_provider_data.xml', None)

        self.Provider._restore_domain_for_action_payment_provider()

        self.assertNotIn('module_to_buy', self.action.domain)
        self.assertIn('company_id', self.action.domain)

        self.action.domain = "[('module_to_buy', '=', False)]"
        self.Provider._restore_domain_for_action_payment_provider()
        self.assertFalse(self.action.domain)
