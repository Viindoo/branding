from markupsafe import Markup

from odoo.addons.web.controllers.database import Database as DB

# De-brand ONLY the Odoo WORDMARK - fixed page-chrome text (the <title>, the
# "insecure database manager" warning-banner copy, the Create Database modal
# privacy notice, and the Restore Database modal copy-detection prompt) -
# NEVER a database NAME the user chose.
#
# The database_manager templates render a database's raw name into two
# places: the visible list label (``t-out="db"``) and the login link's
# ``db=`` query-param (``t-attf-href="/odoo?db={{ db }}"``- see
# odoo/addons/web/static/src/public/database_manager.qweb.html on disk,
# grounded against the actual v19 core template, not from memory).
#
# A generic substring/regex replace over the ENTIRE rendered HTML - even one
# excluding "Odoo" when immediately adjacent to an alnum/``_``/``.``/``-``
# character - still corrupts a database named EXACTLY "Odoo": in
# ``/odoo?db=Odoo``, nothing precedes the "O" but "=" and nothing follows
# the second "o" but the closing quote, neither of which is in the exclusion
# set, so the regex still matches and rewrites the login link to
# ``db=Viindoo`` - a 404 (no such DB), the very login-break the de-brand set
# out to eliminate, only with a narrower trigger (the exact-name case).
#
# Root fix: replace ONLY fixed, LITERAL wordmark strings that appear in
# Odoo's own page chrome (grounded against the actual v19 core templates
# below) - never a templated/data-driven value. Because the mechanism never
# scans for a bare "Odoo" token anywhere, and only replaces specific, known,
# non-db-related literal strings, it cannot rewrite a database name that
# merely CONTAINS (or exactly equals) "Odoo" - "Odoo_prod", "my.Odoo.db" and
# a database named exactly "Odoo" all survive intact. See the residual
# out-of-band edge case documented under "Phrase entries" below.
#
# The allowlist is enumerated by grepping "Odoo" across EVERY template
# ``_render_template`` loads (``database_manager.qweb.html``,
# ``database_manager.master_input.qweb.html``,
# ``database_manager.create_form.qweb.html``) - all FOUR visible wordmark
# sites on /web/database/manager (five raw occurrences, the banner appearing
# in two templates):
#   - web/static/src/public/database_manager.qweb.html:
#     ``<title>Odoo</title>``
#   - web/static/src/public/database_manager.qweb.html (insecure warning
#     banner) and database_manager.master_input.qweb.html (insecure warning
#     banner, reused verbatim by the "Set Master Password", "Restore",
#     "Duplicate", and "Backup" modals): both start with the identical
#     sentence "Warning, your Odoo database manager is not protected." -
#     matched on that shared prefix so both variants are covered by one
#     entry.
#   - web/static/src/public/database_manager.qweb.html, "Create Database"
#     modal (unconditional, no ``t-if`` - renders on every hit): "...some
#     data may be sent to Odoo online services." - matched on the phrase
#     "Odoo online services".
#   - web/static/src/public/database_manager.qweb.html, "Restore Database"
#     modal (unconditional, no ``t-if`` - renders on every hit): "...Odoo
#     needs to know if this database was moved or copied." - matched on the
#     phrase "Odoo needs to know".
#
# Phrase entries and the db-name boundary: the last two entries are matched
# as multi-word PHRASES (including the adjacent prose word, e.g. "Odoo
# online services" rather than a bare "Odoo") specifically so they cannot
# collide with a database name. Any database created THROUGH Odoo satisfies
# ``DBNAME_PATTERN`` (``^[a-zA-Z0-9][a-zA-Z0-9_.-]+$``, enforced by the core
# ``create``/``duplicate`` handlers), which forbids the space character - so
# a phrase entry containing a literal space can never appear inside a "db="
# login link or a db-list label for such a database.
#
# That guarantee has a known boundary: the rendered list comes from
# ``http.db_list()`` -> ``odoo.service.db.list_dbs()``, which returns the raw
# ``datname`` straight out of ``pg_database`` (filtered only for templates
# and the ``dbfilter``) - it never re-validates the name against
# ``DBNAME_PATTERN``. A database created OUT-OF-BAND, bypassing Odoo (e.g.
# ``createdb 'Odoo online services'``), would therefore still be listed and
# its label WOULD be rewritten. This is an accepted residual: such a name is
# already unreachable through Odoo's own create path, and the alternative
# (dropping the phrase entries) would leave a real wordmark on a pre-auth
# page. The one invariant that does hold unconditionally is the
# space-free-name case, which covers every Odoo-created database.
#
# IMPORTANT: this allowlist must stay in sync with the template's visible
# "Odoo" wordmark strings - if a core template update (or a v19 -> vNext
# forward-port) adds, removes, or rewords a visible "Odoo" occurrence on
# /web/database/manager, update this tuple to match. This is ENFORCED, not
# left to a manual re-grep: tests/test_debrand_allowlist_sync.py reads the
# three core templates off disk and fails loudly on any drift (a missing
# ``old`` literal, or a newly added "Odoo" the allowlist does not cover).
_WORDMARK_STRINGS = (
    ('<title>Odoo</title>', '<title>Viindoo</title>'),
    (
        'Warning, your Odoo database manager is not protected',
        'Warning, your Viindoo database manager is not protected',
    ),
    ('Odoo online services', 'Viindoo online services'),
    ('Odoo needs to know', 'Viindoo needs to know'),
)

# Asset / URL substitutions. Same allowlist discipline as the wordmark
# strings above: fixed literals only, never a templated value, and the same
# on-disk sync test guards them.
#
# On the ``img-fluid d-block mx-auto`` entry: this is a cosmetic Bootstrap
# class rewrite that adds vertical margin to the (now Viindoo) logo. It is
# scoped by UNIQUENESS rather than by structure - that class trio occurs
# exactly once across all three templates, on the logo ``<img>`` itself, and
# tests/test_debrand_allowlist_sync.py asserts that it still occurs exactly
# once. If core ever adds the same trio elsewhere on the page, the test
# fails loudly instead of the margin silently landing on every match.
#
# The structural alternative - matching the whole ``<img src=... class=.../>``
# tag - was rejected: the response is lxml-parsed and re-serialized by qweb
# (``html.document_fromstring`` in core's ``_render_template``), so attribute
# order, quoting, and the self-closing form in the OUTPUT are not guaranteed
# to match the template SOURCE byte-for-byte. A full-tag literal could
# therefore silently no-op - the exact failure class this allowlist exists
# to prevent - while buying no additional safety over the uniqueness guard.
_ASSET_STRINGS = (
    ('https://www.odoo.com/privacy', 'https://viindoo.com/policy/privacy-policy'),
    ('/web/static/img/logo2.png', '/viin_brand/static/img/Viindoo-logo.svg'),
    ('img-fluid d-block mx-auto', 'img-fluid d-block mx-auto my-4'),
    ('/web/static/img/favicon.ico', '/viin_brand/static/img/favicon.ico'),
)


class Database(DB):

    def _render_template(self, **d):
        res = super()._render_template(**d)
        if res:
            # ``super()._render_template()`` returns a ``markupsafe.Markup``
            # instance (it delegates to qweb's ``render()``, which returns
            # ``Markup(''.join(...))`` - see odoo/addons/base/models/ir_qweb.py).
            #
            # ``Markup`` overrides ``str.replace()`` to auto-escape, which
            # breaks any entry whose strings contain markup. The exact
            # failure mode differs by markupsafe generation, and BOTH are
            # live in the wild - Odoo 19's requirements.txt pins MarkupSafe
            # 2.x, while a distro-packaged environment may ship 3.x:
            #   - markupsafe 2.x: ``replace`` is built by
            #     ``_simple_escaping_wrapper(str.replace)``, which escapes
            #     EVERY argument, so the search string
            #     ``'<title>Odoo</title>'`` becomes
            #     ``'&lt;title&gt;Odoo&lt;/title&gt;'`` and never matches the
            #     raw HTML - the de-brand silently no-ops on that entry.
            #   - markupsafe 3.x: ``replace()`` escapes only the REPLACEMENT
            #     (``super().replace(old, self.escape(new), count)``), so the
            #     match succeeds but ``'<title>Viindoo</title>'`` is written
            #     back as ``'&lt;title&gt;Viindoo&lt;/title&gt;'`` - visible
            #     escaped markup in the page <title>.
            # Only the ``<title>`` entry is affected either way: it is the
            # single pair whose ``old``/``new`` contain HTML-special
            # characters; escaping is a no-op on every other entry below.
            # Coercing to a plain ``str`` up front makes every ``.replace()``
            # an ordinary literal substring replace under both generations.
            res = str(res)
            for old, new in _WORDMARK_STRINGS + _ASSET_STRINGS:
                res = res.replace(old, new)
            # Restore the contract core's ``_render_template`` publishes: it
            # returns ``Markup``, and so must every override of it. The
            # de-branded body is the same trusted, already-escaped qweb
            # output we received - only fixed literals from the allowlist
            # above were substituted, no dynamic value was interpolated - so
            # re-marking it safe introduces no escaping regression. Returning
            # a bare ``str`` instead would silently drop markupsafe's safety
            # net on a PRE-AUTH page: a later override in the merged
            # controller MRO that composes this result would get no
            # auto-escaping, and it would also leave this method's return
            # type inconsistent (``Markup`` on the falsy branch, ``str``
            # here).
            res = Markup(res)
        return res
