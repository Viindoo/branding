def post_init_hook(env):
    """Replace 'Odoo account' with 'your account' in 2FA invitation email subject."""
    template = env.ref('auth_totp_mail.mail_template_totp_invite', raise_if_not_found=False)
    if template and template.subject and 'Odoo' in template.subject:
        template.subject = template.subject.replace('Odoo account', 'your account')
