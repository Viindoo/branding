def post_init_hook(env):
    """Replace 'Odoo Discuss' with 'Discuss' in calendar mail templates."""
    template_xmlids = [
        'calendar.calendar_template_meeting_invitation',
        'calendar.calendar_template_meeting_changedate',
        'calendar.calendar_template_meeting_reminder',
        'calendar.calendar_template_meeting_update',
    ]
    for xmlid in template_xmlids:
        template = env.ref(xmlid, raise_if_not_found=False)
        if template and template.body_html and 'Odoo Discuss' in template.body_html:
            template.body_html = template.body_html.replace('Odoo Discuss', 'Discuss')
