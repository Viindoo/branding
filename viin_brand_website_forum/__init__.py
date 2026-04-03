def post_init_hook(env):
    if env.ref('website_forum.forum_help', raise_if_not_found=False):
        forum_help = env.ref('website_forum.forum_help')
        forum_help._set_default_faq()
