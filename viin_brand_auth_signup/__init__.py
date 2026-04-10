def post_init_hook(env):
    """Replace Odoo branding in auth_signup email templates."""
    try:
        from odoo.addons.viin_brand import replace_odoo_branding_in_mail_templates
    except ImportError:
        return
    replace_odoo_branding_in_mail_templates(env)
