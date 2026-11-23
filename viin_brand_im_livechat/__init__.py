from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

from . import models

# The colour core gives a new channel for its header and its button.
CORE_DEFAULT_COLOUR = "#875A7B"


def _update_viindoo_livechat_color(env):
    """Give the channels that still hold the stock colours the Viindoo colour.

    Each colour is judged on its own: one the customer chose is left untouched.
    """
    channels = env["im_livechat.channel"].with_context(active_test=False)
    for field_name in ("header_background_color", "button_background_color"):
        channels.search([(field_name, "=", CORE_DEFAULT_COLOUR)]).write({
            field_name: VIINDOO_BRAND_COLOR,
        })


def post_init_hook(env):
    _update_viindoo_livechat_color(env)
