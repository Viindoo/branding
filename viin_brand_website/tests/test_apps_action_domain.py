from odoo.fields import Domain
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import convert_file
from odoo.tools.safe_eval import safe_eval


@tagged('post_install', '-at_install')
class TestAppsActionDomain(TransactionCase):

    def test_enterprise_condition_is_applied_again_after_website_rewrites_the_apps_domain(self):
        Module = self.env['ir.module.module']
        action = self.env.ref('base.open_module_tree')
        theme = Module.create({'name': 'theme_stub', 'state': 'uninstalled'})
        action.domain = "['!', ('name', '=like', 'theme_%')]"

        convert_file(self.env, 'viin_brand_website', 'data/ir_module_module_data.xml', None)

        domain = Domain(safe_eval(action.domain))
        self.assertTrue(any(c.field_expr == 'to_buy' for c in domain.iter_conditions()))
        self.assertFalse(Module.search(domain & Domain('id', '=', theme.id)), "themes stay hidden")
