from odoo.tools.translate import TranslationImporter, get_po_paths


def _force_branding_translations(env):
    """Force-overwrite the translations of this module's own PO files.

    The core records re-declared here are ``noupdate="1"``: a language installed before this
    module keeps the core translation, so the import bypasses that guard for the xmlids of this
    module's PO files only.
    """
    lang_codes = [code for code, _name in env['res.lang'].get_installed() if code != 'en_US']
    if not lang_codes:
        return

    importer = TranslationImporter(env.cr, verbose=False)
    for lang in lang_codes:
        for po_path in get_po_paths('viin_brand_calendar', lang):
            importer.load_file(po_path, lang)
    importer.save(overwrite=True, force_overwrite=True)


def _replace_odoo_discuss_in_calendar_templates(env):
    """Replace 'Odoo Discuss' with 'Discuss' in calendar mail templates."""
    for xmlid in [
        'calendar.calendar_template_meeting_invitation',
        'calendar.calendar_template_meeting_changedate',
        'calendar.calendar_template_meeting_reminder',
        'calendar.calendar_template_meeting_update',
    ]:
        template = env.ref(xmlid, raise_if_not_found=False)
        if template and template.body_html and 'Odoo Discuss' in template.body_html:
            template.body_html = template.body_html.replace('Odoo Discuss', 'Discuss')


def _post_init_hook(env):
    _force_branding_translations(env)
    _replace_odoo_discuss_in_calendar_templates(env)
