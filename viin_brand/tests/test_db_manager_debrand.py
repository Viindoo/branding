from odoo.tests.common import HttpCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestViinBrandDbManagerDebrand(HttpCase):
    """The database-manager pages must be de-branded to Viindoo AND every
    kwarg-driven variant of ``Database._render_template`` must still render.

    The v16 override forwards NO kwargs to ``super()._render_template()``. On
    19.0 core drives the template through ``manage=`` / ``error=`` kwargs
    (``selector()`` -> ``manage=False``; ``create()`` and the other write
    handlers -> ``error=...``), so the dropped ``**d`` renders the wrong
    variant. These tests protect both the de-brand string replacements and the
    kwarg-path rendering behavior.
    """

    def test_db_manager_page_is_debranded_to_viindoo(self):
        """The database-manager page shows Viindoo branding, and EVERY known
        Odoo WORDMARK occurrence (page-chrome text: title, insecure banner,
        Create Database modal privacy notice, Restore Database modal
        copy-detection prompt) is de-branded - checked as specific strings,
        NOT as a blanket "no 'Odoo' substring anywhere" ban.

        Root cause of the narrowed assertion: the DB manager page lists
        every database visible on this Postgres server
        (``http.db_list()``). By design (see ``controllers/database.py``),
        a database NAME containing "Odoo" is intentionally left intact - so
        a blanket ``assertNotIn('Odoo', body)`` flakes any time a sibling DB
        happens to be named with "Odoo" in it, even though nothing is wrong
        with the de-brand. Asserting on the specific wordmark strings keeps
        this test able to fail on a real de-brand regression while dropping
        the false-positive trigger.

        Coverage note: a HIGH re-review found the allowlist covered only 2
        of the 4 wordmark occurrences that actually render on this page -
        the Create Database and Restore Database modals (unconditional, no
        ``t-if``, always present) were missed. This test now asserts all 4,
        each as a Viindoo-form-present AND Odoo-form-absent pair.
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
        # No residual Odoo WORDMARK (page chrome) - specific strings, not a
        # blanket substring ban (see docstring above for why).
        self.assertNotIn(
            '<title>Odoo</title>', body,
            "the page <title> must not still read the bare Odoo wordmark",
        )
        self.assertNotIn(
            '/web/static/img/logo2.png', body,
            "the core Odoo logo asset must be replaced by the Viindoo logo",
        )

        # Insecure warning banner (and its "Set Master Password"/"Restore"/
        # "Duplicate"/"Backup" modal reuse via master_input) - renders only
        # when the instance has no master password set, so the POSITIVE
        # direction cannot be asserted outright. The NEGATIVE direction can,
        # and is the one that protects the user: an Odoo wordmark must never
        # ship on this pre-auth page, whether or not the banner renders.
        #
        # This assertion is deliberately UNCONDITIONAL. It used to sit
        # inside ``if 'database manager is not protected' in body:`` - a
        # guard keyed on a string CORE owns. If core ever reworded the
        # banner, the allowlist in controllers/database.py would stop
        # matching AND that guard would go False, so both the assertIn and
        # the assertNotIn were silently skipped: an Odoo wordmark would ship
        # with a fully green suite. Never "skip if absent".
        #
        # The reword case itself is covered by a separate, always-running
        # static guard: tests/test_debrand_allowlist_sync.py reads the core
        # templates off disk and fails when an allowlist ``old`` literal no
        # longer exists (or a new "Odoo" appears). The two together close
        # the hole - the static test catches the reword, this test catches
        # the leak.
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

        The invalid name posted below makes core's ``create`` raise + log its
        "Database creation error." traceback at ERROR by design (it is caught and
        re-rendered as the error page). That expected-error log is muted so it is
        not mistaken for a real failure by a log scraper - mirroring how core's own
        ``test_ir_module`` mutes ``odoo.modules.module`` for its error-path tests.

        Guards that the ``error=`` kwarg reaches ``super()._render_template`` -
        list_db-independent because the template's ``<t t-if="error">`` block is
        rendered regardless of the database-list state. The POST is
        side-effect-free: an empty ``master_pwd`` short-circuits the admin-password
        change and the invalid name raises before any database operation runs.
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
