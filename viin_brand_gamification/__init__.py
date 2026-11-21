def post_init_hook(env):
    """Point the "Powered by" footer of the badge mail to Viindoo.

    The catalog of this module loads before this hook writes the English it translates, so the
    catalog is applied again once that English is written.
    """
    template = env.ref('gamification.email_template_badge_received', raise_if_not_found=False)
    if template:
        # the stored value is a Markup, whose replace() would escape the markup of its arguments
        body = str(template.body_html)
        template.body_html = body.replace('https://www.odoo.com', 'https://viindoo.com').replace(
            '>Odoo</a>', '>Viindoo</a>',
        )
        env['ir.module.module']._reapply_noupdate_translations('viin_brand_gamification')
