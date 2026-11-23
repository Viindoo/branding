from markupsafe import Markup

from odoo.addons.web.controllers import database as web_database

# Replaces only the fixed wordmark literals of the database manager chrome: the <title>, the
# insecure-manager warning banner, the Create Database privacy notice and the Restore Database
# prompt. A database name is never rewritten: the templates render it in the visible list and in
# the ``db=`` query parameter of the login link, and a regex over the whole page would turn a
# database named exactly "Odoo" into a 404 link.
#
# The two phrase entries ("Odoo online services", "Odoo needs to know") contain a space, which a
# database name created through Odoo cannot (``DBNAME_PATTERN``). A database created outside Odoo
# with such a name would be rewritten in the list; that residual is accepted.
#
# Every entry must match a visible "Odoo" string of the three core templates
# (``database_manager.qweb.html``, ``database_manager.master_input.qweb.html`` and
# ``database_manager.create_form.qweb.html``); tests/test_debrand_allowlist_sync.py reads them off
# disk and fails on drift.
_WORDMARK_STRINGS = (
    ('<title>Odoo</title>', '<title>Viindoo</title>'),
    (
        'Warning, your Odoo database manager is not protected',
        'Warning, your Viindoo database manager is not protected',
    ),
    ('Odoo online services', 'Viindoo online services'),
    ('Odoo needs to know', 'Viindoo needs to know'),
)

# Asset and URL literals, under the same allowlist discipline. The ``img-fluid d-block mx-auto``
# entry adds a vertical margin to the logo; the class trio occurs once across the templates, on
# the logo itself, and the sync test asserts that. Matching the whole ``<img>`` tag is not
# possible: qweb re-serialises the markup, so attribute order and quoting are not stable.
_ASSET_STRINGS = (
    ('https://www.odoo.com/privacy', 'https://viindoo.com/policy/privacy-policy'),
    ('/web/static/img/logo2.png', '/viin_brand/static/img/Viindoo-logo.svg'),
    ('img-fluid d-block mx-auto', 'img-fluid d-block mx-auto my-4'),
    ('/web/static/img/favicon.ico', '/viin_brand/static/img/favicon.ico'),
)


def _brand_template(render_template):
    """Wrap the database manager renderer of ``web`` so that the page names Viindoo.

    :param render_template: ``web.controllers.database._render_template``
    :return: the renderer to put in its place
    """
    def _render_branded_template(**d):
        res = render_template(**d)
        if res:
            # Markup.replace escapes its arguments (markupsafe 2.x) or the replacement
            # (markupsafe 3.x), which breaks the ``<title>`` entry; replace on a plain str.
            res = str(res)
            for old, new in _WORDMARK_STRINGS + _ASSET_STRINGS:
                res = res.replace(old, new)
            # Only allowlisted literals were substituted, so the body is as trusted as core's.
            res = Markup(res)
        return res

    return _render_branded_template


def patch_database_manager():
    """Brand the page of every database manager route; core's controller calls the renderer by its module name."""
    web_database._render_template = _brand_template(web_database._render_template)
