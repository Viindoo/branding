from odoo import tools
from . import models
from . import wizard

try:
    from odoo.addons.test_discuss_full.tests.test_performance import TestDiscussFullPerformance
    _get_init_messaging_result_original = TestDiscussFullPerformance._get_init_messaging_result
except ImportError:
    TestDiscussFullPerformance = None
    _get_init_messaging_result_original = None


def _get_init_messaging_result_plus(self):
    res = _get_init_messaging_result_original(self)
    if 'odoobot' in res and res['odoobot']:
        res['odoobot']['name'] = 'ViindooBot'
        res['odoobot']['email'] = 'viindoobot@example.viindoo.com'
    return res


def post_load():
    if TestDiscussFullPerformance and _get_init_messaging_result_original:
        TestDiscussFullPerformance._get_init_messaging_result = _get_init_messaging_result_plus


def post_init_hook(env):
    if tools.config.get('test_enable', False) and env.ref('base.partner_root', raise_if_not_found=False):
        env.ref('base.partner_root').write({'name': 'OdooBot', 'email': 'odoobot@example.com'})
