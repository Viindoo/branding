from . import controllers


def replace_odoo_branding_in_mail_templates(env):
    """Replace Odoo branding in all mail.template body_html and subject (jsonb) via raw SQL.

    ORM write on Html fields with translate=True doesn't reliably replace
    link text inside sanitized HTML. Raw SQL on jsonb::text bypasses this.

    This function is idempotent - safe to call from multiple post_init_hooks.
    The last branding module to install catches all remaining templates.
    """
    # Order matters: specific patterns first, generic catch-all last.
    replacements = [
        ('https://www.odoo.com/page/tour', 'https://viindoo.com/page/viindoo-solution'),
        ('https://www.odoo.com', 'https://viindoo.com'),
        ('http://yourcompany.odoo.com', 'http://yourcompany.viindoo.com'),
        ('>Odoo Tour</a>', '>Viindoo Tour</a>'),
        ('>Odoo</a>', '>Viindoo</a>'),
        ('alt="Odoo"', 'alt="Viindoo"'),
        # Generic catch-all (must be last)
        ('Odoo', 'Viindoo'),
    ]
    for old, new in replacements:
        env.cr.execute(
            "UPDATE mail_template SET body_html = REPLACE(body_html::text, %s, %s)::jsonb"
            " WHERE body_html::text LIKE %s",
            (old, new, f'%{old}%'),
        )
    # Also replace in subject field
    env.cr.execute(
        "UPDATE mail_template SET subject = REPLACE(subject::text, 'Odoo', 'Viindoo')::jsonb"
        " WHERE subject::text LIKE '%%Odoo%%'",
    )
