from unittest.mock import patch

from markupsafe import Markup

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.web.controllers.database import Database as CoreDatabase
from ..controllers.database import Database as ViinBrandDatabase


# Stand-in for the qweb-rendered database_manager.qweb.html output: the Odoo wordmark appears in
# page chrome (title, warning banner), while databases named "Odoo_prod", "my.Odoo.db" and exactly
# "Odoo" appear as list content, in their visible text and in their "/odoo?db=..." login link.
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
    """The de-brand override must never corrupt a database NAME that contains (or
    exactly equals) the substring "Odoo" (e.g. "Odoo_prod", "my.Odoo.db", or a
    database named exactly "Odoo") - only the Odoo wordmark in page chrome may be
    rewritten to Viindoo.

    A blanket ``replace('Odoo', 'Viindoo')`` would rewrite the visible list text and
    the "/odoo?db=..." login link of such a database, breaking login to it; so would
    a boundary-based regex for a database named exactly "Odoo". The override
    (``controllers/database.py``) replaces only fixed literal wordmark strings.

    The CORE parent method
    (``odoo.addons.web.controllers.database.Database._render_template``) is stubbed
    to return a controlled HTML fixture and the real override is called directly:
    no HTTP round-trip and no dependency on any real database name.
    """

    def _render(self):
        # The fixture is a ``Markup``, as core's ``_render_template`` returns one. A plain
        # ``str`` would bypass the ``str(res)`` coercion in the override, which is needed
        # because ``Markup.replace()`` auto-escapes (2.x escapes the search string so it never
        # matches; 3.x escapes the replacement so it renders as visible entities).
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
        database.
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

        The safety rule holds for any DB-name shape, not just one separator
        character.
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

        A boundary-based regex excluding "Odoo" only when adjacent to a
        db-name-valid character still matches here (``=`` and the closing quote
        are not db-name-valid characters), rewriting the login link to
        ``db=Viindoo`` - a 404, since no database named "Viindoo" exists.
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
