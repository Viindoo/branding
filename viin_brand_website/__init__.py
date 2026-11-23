import ast

from odoo.fields import Domain

from odoo.addons.viin_brand.models.ir_module_module import _is_to_buy_condition

from . import models


def _brand_untouched_favicons(env):
    """Give the Viindoo favicon to the websites that still carry core's stock one.

    A field default applies only when a record is created, so it never reaches
    ``base.default_website`` (created while ``website`` loads). Only a favicon
    byte-identical to core's default is replaced; any other value was chosen by
    someone and is kept.
    """
    Website = env['website']
    core_default = bytes(Website._default_favicon())
    untouched = Website.search([]).filtered(lambda website: website.favicon and bytes(website.favicon) == core_default)
    untouched.write({'favicon': Website._default_brand_favicon()})


def post_init_hook(env):
    _brand_untouched_favicons(env)


def uninstall_hook(env):
    """Give the Apps list of the website its own domain back.

    Only the Enterprise-stub condition is dropped, so the themes stay hidden from the list.
    """
    action = env.ref('website.action_website_add_features', raise_if_not_found=False)
    if action and action.domain:
        domain = Domain(ast.literal_eval(action.domain)).map_conditions(
            lambda condition: Domain.TRUE if _is_to_buy_condition(condition) else condition,
        )
        action.domain = False if domain.is_true() else repr(domain)
