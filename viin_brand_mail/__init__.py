from . import models
from . import wizard
from odoo.tests.common import TransactionCase
setupTransactionCase = TransactionCase.setUp


def _setupTransactionCase_plus(self):
    """Odoo has some test cases to check the return value when the Odoo bot performs an action
    Some tests like:
    - test_manual_revaluation_statement
    Therefore, it is necessary to check if the Odoo bot is being rebranded as the Viindoo bot
    Change the name and email of the Odoo bot if necessary
    """
    res = setupTransactionCase(self)
    bot = self.env.ref('base.partner_root', raise_if_not_found=False)
    if bot.name == 'ViindooBot' or bot.email == 'viindoobot@example.viindoo.com':
        bot.write({
            'name': 'OdooBot',
            'email': 'odoobot@example.com'
        })
    return res


def _post_init_hook(env):
    TransactionCase.setUp = _setupTransactionCase_plus
