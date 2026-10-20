# Part of Odoo. See LICENSE file for full copyright and licensing details.


def activate_frontend_lang(env, code):
    """Activate ``code`` and make it a language a public visitor can pick."""
    lang = env["res.lang"]._activate_lang(code)
    if "website" in env:
        # with website installed, a visitor language must be one of the website's languages
        env["website"].search([]).write({"language_ids": [(4, lang.id)]})
    return lang
