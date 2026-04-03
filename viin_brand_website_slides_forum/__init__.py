def post_init_hook(env):
    forums = env['forum.forum']
    if env.ref('website_slides_forum.forum_forum_demo_channel_0', raise_if_not_found=False):
        forums |= env.ref('website_slides_forum.forum_forum_demo_channel_0')
    if env.ref('website_slides_forum.forum_forum_demo_channel_2', raise_if_not_found=False):
        forums |= env.ref('website_slides_forum.forum_forum_demo_channel_2')
    if forums:
        forums._set_default_faq()
