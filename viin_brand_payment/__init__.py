from . import models
from . import wizards


def uninstall_hook(env):
    env['payment.provider']._restore_domain_for_action_payment_provider()
