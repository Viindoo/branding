from . import models


def post_init_hook(env):
    forum_help = env.ref('website_forum.forum_help', raise_if_not_found=False)
    if forum_help:
        forum_help._set_default_faq_all_langs()
