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
        for po_path in get_po_paths('viin_brand_auth_signup', lang):
            importer.load_file(po_path, lang)
    importer.save(overwrite=True, force_overwrite=True)
