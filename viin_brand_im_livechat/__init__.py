from . import models


def _update_viindoo_livechat_color(env):
    livechat_channels = env["im_livechat.channel"].with_context(active_test=False).search([])
    if livechat_channels:
        livechat_channels.write({
            "header_background_color": "#00a4b5",
            "button_background_color": "#7f4282",
        })


def post_init_hook(env):
    _update_viindoo_livechat_color(env)
