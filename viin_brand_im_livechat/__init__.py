from . import models

# NOTE: `im_livechat.tests.test_message.TestImLivechatMessage.test_feedback_message` and
# `.test_message_to_store` assert a `module_icon` key (routed through
# `MailCommon._filter_threads_fields`) that this Viindoo de-brand stack legitimately changes
# from the stock `/mail/static/description/icon.png` to the branded icon path. That
# expectation is already realigned - not neutered - by `to_base`'s
# `_patch_mailcommon_module_icon_expectation()` (tvtmaaddons_19.0/to_base/__init__.py), which
# names both of these exact tests in its own docstring and rewrites the expected
# `module_icon` value via the same resolver the Store uses, leaving every other assertion in
# both tests (session creation, bus notifications, rating flow, Store payload shape) live. No
# module-local patch is needed here.


def _update_viindoo_livechat_color(env):
    livechat_channels = env["im_livechat.channel"].with_context(active_test=False).search([])
    if livechat_channels:
        livechat_channels.write({
            "header_background_color": "#00a4b5",
            "button_background_color": "#7f4282",
        })


def post_init_hook(env):
    _update_viindoo_livechat_color(env)
