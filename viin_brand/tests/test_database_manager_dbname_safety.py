from unittest.mock import patch

from markupsafe import Markup

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.web.controllers.database import Database as CoreDatabase
from ..controllers.database import Database as ViinBrandDatabase


# A controlled fixture standing in for the real qweb-rendered
# database_manager.qweb.html output: the Odoo WORDMARK appears in page
# chrome (title, warning banner), while databases the user named "Odoo_prod",
# "my.Odoo.db", and - the narrowest, most severe case - exactly "Odoo" (a
# bare token with no adjacent alnum/._- character) all appear as plain list
# content - both in their visible text and inside their "/odoo?db=..." login
# link.
FIXTURE_HTML = """<!DOCTYPE html>
<html>
<head><title>Odoo</title></head>
<body>
<div class="alert alert-warning">
    Warning, your Odoo database manager is not protected.
</div>
<ul class="list-group">
    <li class="list-group-item">
        <a href="/odoo?db=Odoo_prod" class="d-block flex-grow-1">
            <span>Odoo_prod</span>
        </a>
    </li>
    <li class="list-group-item">
        <a href="/odoo?db=my.Odoo.db" class="d-block flex-grow-1">
            <span>my.Odoo.db</span>
        </a>
    </li>
    <li class="list-group-item">
        <a href="/odoo?db=Odoo" class="d-block flex-grow-1">
            <span>Odoo</span>
        </a>
    </li>
</ul>
</body>
</html>
"""


@tagged('post_install', '-at_install')
class TestViinBrandDbNameSafety(TransactionCase):
    """The de-brand override must never corrupt a database NAME token that
    happens to contain (or exactly equal) the substring "Odoo" (e.g.
    "Odoo_prod", "my.Odoo.db", or a database named exactly "Odoo") - only the
    Odoo WORDMARK (page chrome: title, headings, warning/"powered by"-style
    copy) may be rewritten to Viindoo.

    History of root causes fixed here:

    1. The original bug: ``_render_template`` did a blanket
       ``res.replace('Odoo', 'Viindoo')`` over the ENTIRE rendered HTML,
       rewriting a database named e.g. "Odoo_prod" to "Viindoo_prod" - in
       both the visible database-list text AND its "/odoo?db=Odoo_prod"
       login link - silently breaking login to that database.
    2. A narrower re-review finding: replacing the blanket ``.replace()``
       with a boundary-based regex (``(?<![A-Za-z0-9_.-])Odoo(?![A-Za-z0-9_.-])``)
       still corrupted a database named EXACTLY "Odoo" - in
       ``/odoo?db=Odoo`` nothing precedes/follows "Odoo" but "=" and the
       closing quote, neither of which is excluded by the regex, so it still
       matched and rewrote the login link to the non-existent "Viindoo" DB.

    The current mechanism (see ``controllers/database.py``) replaces ONLY
    two fixed, literal wordmark strings (``<title>Odoo</title>`` and the
    "Warning, your Odoo database manager is not protected" banner prefix) -
    a positive allowlist that never scans for a bare "Odoo" token anywhere,
    so it cannot touch a database name regardless of what that name is.

    This test stubs the CORE parent method
    (``odoo.addons.web.controllers.database.Database._render_template``,
    the one viin_brand's ``Database`` subclasses) to return a controlled
    HTML fixture, then calls the real viin_brand override directly. No live
    HTTP round-trip, no demo data, no dependency on any real database
    actually being named with "Odoo" in it.
    """

    def _render(self):
        # The fixture is returned as a ``Markup``, not a plain ``str``,
        # because that is what core's ``_render_template`` actually returns
        # (qweb's ``render()`` returns ``Markup(''.join(...))`` - see
        # odoo/addons/base/models/ir_qweb.py). Stubbing a plain ``str`` here
        # made these tests bypass the ``Markup`` path entirely: the
        # ``str(res)`` coercion in the override could be deleted and all
        # four tests stayed green, even though ``Markup.replace()``
        # auto-escaping breaks the ``<title>`` de-brand on every markupsafe
        # generation (2.x escapes the search string so it never matches;
        # 3.x escapes the replacement so it renders as visible entities).
        with patch.object(CoreDatabase, '_render_template', return_value=Markup(FIXTURE_HTML)):
            return ViinBrandDatabase()._render_template()

    def test_wordmark_is_debranded_to_viindoo(self):
        """The Odoo wordmark (page chrome) must still be de-branded to Viindoo."""
        res = self._render()
        self.assertIn(
            '<title>Viindoo</title>', res,
            "the page <title> wordmark must be de-branded to Viindoo",
        )
        self.assertIn(
            'your Viindoo database manager is not protected', res,
            "the warning-banner wordmark copy must be de-branded to Viindoo",
        )

    def test_database_name_containing_odoo_is_left_intact(self):
        """A database literally named "Odoo_prod" must never be rewritten.

        Neither its visible list text nor its /odoo?db=... login link may be
        touched - rewriting either one silently breaks login to that
        database (the review's own worked example).
        """
        res = self._render()
        self.assertIn(
            'href="/odoo?db=Odoo_prod"', res,
            "the DB name token inside the /odoo?db=... login link must stay "
            "'Odoo_prod' unchanged",
        )
        self.assertIn(
            '>Odoo_prod<', res,
            "the DB name token in the visible list text must stay "
            "'Odoo_prod' unchanged",
        )
        self.assertNotIn(
            'Viindoo_prod', res,
            "a database named 'Odoo_prod' must never be silently rewritten "
            "to 'Viindoo_prod'",
        )

    def test_database_name_with_dot_adjacent_odoo_is_left_intact(self):
        """A dot-adjacent DB-name variant ("my.Odoo.db") is left intact too.

        Strengthens the contract beyond the underscore-only worked example:
        the safety rule must hold for any DB-name shape, not just one
        separator character.
        """
        res = self._render()
        self.assertIn(
            'href="/odoo?db=my.Odoo.db"', res,
            "the dot-adjacent DB name token inside the login link must stay "
            "'my.Odoo.db' unchanged",
        )
        self.assertIn(
            '>my.Odoo.db<', res,
            "the dot-adjacent DB name token in the visible list text must "
            "stay 'my.Odoo.db' unchanged",
        )
        self.assertNotIn(
            'my.Viindoo.db', res,
            "a database named 'my.Odoo.db' must never be silently rewritten "
            "to 'my.Viindoo.db'",
        )

    def test_database_name_exactly_odoo_is_left_intact(self):
        """A database literally named "Odoo" (a bare token, with no
        adjacent alnum/``_``/``.``/``-`` character) must never be rewritten.

        This is the narrowest and most severe trigger: a boundary-based
        regex excluding "Odoo" only when adjacent to a db-name-valid
        character still matches here (``=`` and the closing quote are not
        db-name-valid characters), rewriting the login link to
        ``db=Viindoo`` - a 404, since no database named "Viindoo" exists.
        That is the exact login-break the de-brand set out to eliminate,
        just with a narrower trigger than "Odoo_prod".
        """
        res = self._render()
        self.assertIn(
            'href="/odoo?db=Odoo"', res,
            "the login link for a database named exactly 'Odoo' must "
            "survive de-brand intact - rewriting it to 'db=Viindoo' 404s "
            "because no such database exists",
        )
        self.assertIn(
            '>Odoo<', res,
            "the visible list label for a database named exactly 'Odoo' "
            "must survive de-brand intact",
        )
