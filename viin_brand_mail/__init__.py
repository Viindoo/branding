from odoo import tools
from . import models
from . import wizard


def post_load():
    """Patch MailCommon.setUpClass to revert ViindooBot back to OdooBot for tests.

    In the post-install test workflow, modules are installed without --test-enable,
    so post_init_hook (which reverts ViindooBot→OdooBot) is skipped. The DB keeps
    ViindooBot but Odoo tests expect OdooBot.

    Solution: patch MailCommon.setUpClass to revert partner_root at the start of
    each test class, when env is available. This covers all test classes that
    inherit from MailCommon.
    """
    if not tools.config.get('test_enable', False):
        return
    try:
        from odoo.addons.mail.tests.common import MailCommon
    except ImportError:
        return

    _original_setUpClass = MailCommon.setUpClass.__func__

    @classmethod
    def _patched_setUpClass(cls):
        _original_setUpClass(cls)
        cls.partner_root.write({'name': 'OdooBot', 'email': 'odoobot@example.com'})

    MailCommon.setUpClass = _patched_setUpClass


def post_init_hook(env):
    if tools.config.get('test_enable', False) and env.ref('base.partner_root', raise_if_not_found=False):
        env.ref('base.partner_root').write({'name': 'OdooBot', 'email': 'odoobot@example.com'})
