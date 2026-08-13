from odoo.tools.translate import TranslationImporter, get_po_paths


_MODULE_NAME = 'viin_brand_calendar'

_CALENDAR_MAIL_TEMPLATE_XMLIDS = [
    'calendar.calendar_template_meeting_invitation',
    'calendar.calendar_template_meeting_changedate',
    'calendar.calendar_template_meeting_reminder',
    'calendar.calendar_template_meeting_update',
]


def _force_branding_translations(env):
    """Force-overwrite translations shipped by this branding module.

    Why: core records we re-declare (e.g. ``calendar.calendar_template_meeting_invitation``)
    are ``noupdate="1"``. When a target language was installed *before* this branding
    module, the core translation for that record is already in the DB; the standard
    PO import keeps it because of the noupdate guard
    (odoo/tools/translate.py :: TranslationImporter.save). We bypass that guard only
    for xmlids present in this module's own PO files.
    """
    lang_codes = [code for code, _name in env['res.lang'].get_installed() if code != 'en_US']
    if not lang_codes:
        return

    importer = TranslationImporter(env.cr, verbose=False)
    for lang in lang_codes:
        for po_path in get_po_paths(_MODULE_NAME, lang):
            importer.load_file(po_path, lang)
    importer.save(overwrite=True, force_overwrite=True)


def _replace_odoo_discuss_in_calendar_templates(env):
    """Replace 'Odoo Discuss' with 'Discuss' in calendar mail templates."""
    for xmlid in _CALENDAR_MAIL_TEMPLATE_XMLIDS:
        template = env.ref(xmlid, raise_if_not_found=False)
        if template and template.body_html and 'Odoo Discuss' in template.body_html:
            template.body_html = template.body_html.replace('Odoo Discuss', 'Discuss')


def _post_init_hook(env):
    _force_branding_translations(env)
    _replace_odoo_discuss_in_calendar_templates(env)
