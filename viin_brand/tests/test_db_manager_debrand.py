from odoo.tests.common import HttpCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestViinBrandDbManagerDebrand(HttpCase):
    """The database-manager pages must be de-branded to Viindoo AND every
    kwarg-driven variant of ``Database._render_template`` must still render.

    Core drives the template through ``manage=`` / ``error=`` kwargs
    (``selector()`` -> ``manage=False``; ``create()`` and the other write
    handlers -> ``error=...``), so the override must forward them to
    ``super()._render_template()``. These tests protect both the de-brand string
    replacements and the kwarg-path rendering.
    """

    def test_db_manager_page_is_debranded_to_viindoo(self):
        """The database-manager page shows Viindoo branding, and every known
        Odoo wordmark occurrence (title, insecure banner, Create Database modal
        privacy notice, Restore Database modal copy-detection prompt) is
        de-branded - checked as specific strings, not as a blanket "no 'Odoo'
        substring anywhere" ban.

        The page lists every database visible on the Postgres server
        (``http.db_list()``) and a database NAME containing "Odoo" is
        intentionally left intact (see ``controllers/database.py``), so a
        blanket ``assertNotIn('Odoo', body)`` would flake on a sibling database
        named with "Odoo".
        """
        res = self.url_open('/web/database/manager')
        self.assertEqual(res.status_code, 200)
        body = res.text
        # De-branded to Viindoo
        self.assertIn('Viindoo', body, "the DB manager must be de-branded to 'Viindoo'")
        self.assertIn(
            '<title>Viindoo</title>', body,
            "the page <title> wordmark must be de-branded to 'Viindoo'",
        )
        self.assertIn(
            '/viin_brand/static/img/Viindoo-logo.svg', body,
            "the DB manager must use the Viindoo logo asset",
        )
        self.assertIn(
            'viindoo.com/policy/privacy-policy', body,
            "the DB manager privacy link must point at Viindoo",
        )
        # No residual Odoo wordmark in the page chrome (specific strings, see docstring).
        self.assertNotIn(
            '<title>Odoo</title>', body,
            "the page <title> must not still read the bare Odoo wordmark",
        )
        self.assertNotIn(
            '/web/static/img/logo2.png', body,
            "the core Odoo logo asset must be replaced by the Viindoo logo",
        )

        # The insecure warning banner renders only when the instance has no master
        # password set, so only the negative direction can be asserted outright.
        # It is unconditional: a guard keyed on a string core owns would be skipped
        # when core rewords the banner, letting an Odoo wordmark ship on this
        # pre-auth page. The reword itself is caught by
        # tests/test_debrand_allowlist_sync.py.
        self.assertNotIn(
            'Warning, your Odoo database manager is not protected', body,
            "the insecure warning-banner wordmark must not still read 'Odoo' - "
            "if this banner was reworded upstream, "
            "tests/test_debrand_allowlist_sync.py will say so",
        )
        self.assertTrue(
            'Warning, your Viindoo database manager is not protected' in body
            or 'database manager is not protected' not in body,
            "the insecure warning banner rendered but not in its de-branded "
            "'Viindoo' form",
        )

        # Create Database modal privacy notice - unconditional (no t-if),
        # always renders on /web/database/manager.
        self.assertIn(
            'some data may be sent to Viindoo online services', body,
            "the Create Database modal privacy notice must be de-branded to "
            "'Viindoo online services'",
        )
        self.assertNotIn(
            'some data may be sent to Odoo online services', body,
            "the Create Database modal privacy notice must not still read "
            "'Odoo online services'",
        )

        # Restore Database modal copy-detection prompt - unconditional (no
        # t-if), always renders on /web/database/manager.
        self.assertIn(
            'Viindoo needs to know if this database was moved or copied', body,
            "the Restore Database modal copy-detection prompt must be "
            "de-branded to 'Viindoo needs to know'",
        )
        self.assertNotIn(
            'Odoo needs to know if this database was moved or copied', body,
            "the Restore Database modal copy-detection prompt must not "
            "still read 'Odoo needs to know'",
        )

    @mute_logger("odoo.addons.web.controllers.database")
    def test_db_create_error_is_rendered_on_the_page(self):
        """A failed DB create re-renders the manager WITH the error alert.

        The invalid name posted below makes core's ``create`` raise and log its
        "Database creation error." traceback at ERROR; it is caught and re-rendered
        as the error page, and the expected log is muted.

        Guards that the ``error=`` kwarg reaches ``super()._render_template``; the
        template's ``<t t-if="error">`` block renders regardless of the database
        list. The POST is side-effect-free: an empty ``master_pwd`` short-circuits
        the admin-password change and the invalid name raises before any database
        operation runs.
        """
        res = self.url_open('/web/database/create', data={
            'master_pwd': '',
            'name': 'invalid name with spaces',
            'lang': 'en_US',
            'password': 'x',
            'login': 'admin',
            'phone': '',
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(
            'Database creation error', res.text,
            "the create-error page must render the error alert; the error= kwarg "
            "must be forwarded to super()._render_template",
        )

    def test_db_selector_suppresses_management_actions(self):
        """The selector page (manage=False) hides the per-database management actions.

        Guards that the ``manage=False`` kwarg reaches ``super()._render_template``.
        Self-calibrating: the ``manage`` flag is only observable when a database is
        listed, so the assertion runs only after confirming the manager page (manage
        default True) actually renders the management actions.
        """
        manager_body = self.url_open('/web/database/manager').text
        if '.o_database_backup' not in manager_body:
            self.skipTest(
                "no database listed / db-manager disabled: the manage flag has no "
                "observable effect on the rendered page"
            )
        selector_body = self.url_open('/web/database/selector').text
        self.assertNotIn(
            '.o_database_backup', selector_body,
            "manage=False (selector page) must suppress the per-database management "
            "actions that the manager page shows",
        )
