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
    # The restore itself lives in `models/res_partner.py` and is driven from
    # `data/res_partner_data.xml`, which runs on install AND on update. This hook only keeps the
    # install path covered without restating the logic.
    env['res.partner']._viin_brand_restore_bot_test_identity()
