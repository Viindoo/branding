import inspect
import re

from odoo.tests.common import BaseCase, tagged
from odoo.tools.misc import file_open

from odoo.addons.web.controllers.database import Database as CoreDatabase
from ..controllers.database import _ASSET_STRINGS, _WORDMARK_STRINGS

# Case-sensitive: the WORDMARK is the capitalised brand token. Lowercase
# "odoo" is deliberately NOT counted - it is structural, not branding, and
# must survive de-brand untouched: the login route ``/odoo?db={{ db }}`` and
# the core asset paths ``/web/static/...``. Rewriting those breaks login and
# 404s the assets. The one lowercase site that IS branding - the
# ``www.odoo.com`` privacy link - is covered separately by
# ``test_odoo_com_links_are_all_covered`` below.
_WORDMARK_TOKEN = 'Odoo'

# How the allowlist is meant to relate to the templates, asserted below:
# every ``old`` literal must still exist on disk, and the wordmark
# occurrences the allowlist accounts for must be ALL of them.
_FIX_HINT = (
    "Update the allowlist in viin_brand/controllers/database.py to match the "
    "current core templates, then re-run this test. Do NOT relax this test - "
    "it is the only thing standing between a core template change and an "
    "Odoo wordmark shipping on the pre-auth database-manager page."
)


@tagged('post_install', '-at_install')
class TestViinBrandDebrandAllowlistSync(BaseCase):
    """The de-brand allowlist must stay in sync with the CORE templates.

    ``controllers/database.py`` de-brands the database manager by replacing a
    positive allowlist of fixed literal strings. That design is deliberate
    (a blanket "Odoo" -> "Viindoo" replace corrupts database NAMES - see
    test_database_manager_dbname_safety.py), but it has one structural
    weakness: an allowlist is only as good as its sync with the templates it
    targets. Two ways it silently rots, both ending with an Odoo wordmark on
    a PRE-AUTH page while the whole suite stays green:

    1. Core REWORDS an existing string -> the ``old`` literal stops matching,
       that replacement no-ops.
    2. Core ADDS a new "Odoo" occurrence -> the allowlist simply never knew
       about it.

    Neither is caught by the HTTP tests: they assert on the specific strings
    this same allowlist already knows about, so they are blind in exactly the
    same places. The code comment used to ask a human to "re-grep every
    template for Odoo to confirm completeness" - an SSOT with no enforcement.
    This test IS that enforcement.

    It is fully static: no database, no HTTP round-trip, no running instance.
    It reads the core templates off the addons path with ``file_open`` and
    compares them against the allowlist tuples imported from the controller
    (imported, never re-typed - the controller stays the single source of
    truth).
    """

    @classmethod
    def _core_template_paths(cls):
        """Return the template paths CORE's ``_render_template`` actually loads.

        Read out of core's own source rather than hardcoded here, so that a
        core change that adds a FOURTH template widens this test's scope
        automatically instead of leaving the new file unchecked.
        """
        source = inspect.getsource(CoreDatabase._render_template)
        return re.findall(r"""file_open\(\s*["']([^"']+\.qweb\.html)["']""", source)

    @classmethod
    def _core_template_source(cls):
        """Concatenated raw source of every template core renders."""
        paths = cls._core_template_paths()
        return ''.join(cls._read(path) for path in paths), paths

    @staticmethod
    def _read(path):
        with file_open(path, 'r') as fdesc:
            return fdesc.read()

    def test_core_templates_are_discoverable(self):
        """Core still loads its database-manager templates via ``file_open``.

        Guards the discovery mechanism the rest of this test file rests on:
        if core stops loading templates this way, the regex silently returns
        an empty list and every downstream assertion passes vacuously.
        """
        paths = self._core_template_paths()
        self.assertTrue(
            paths,
            "could not discover any *.qweb.html template in the source of "
            "odoo.addons.web.controllers.database.Database._render_template - "
            "core changed how it loads the database-manager templates, so the "
            "de-brand allowlist can no longer be verified against them. "
            + _FIX_HINT,
        )
        for path in paths:
            self.assertTrue(
                self._read(path),
                "core template %s is empty or unreadable" % path,
            )

    def test_every_allowlist_target_still_exists_in_core(self):
        """Every ``old`` literal the override replaces must exist on disk.

        Catches rot mode 1 (core reworded a string): a missing ``old`` means
        that replacement silently no-ops in production and the corresponding
        Odoo string ships un-de-branded.
        """
        source, paths = self._core_template_source()
        for old, new in _WORDMARK_STRINGS + _ASSET_STRINGS:
            self.assertIn(
                old, source,
                "the de-brand allowlist entry %r -> %r no longer matches "
                "anything in the core templates %s. Core reworded or removed "
                "it, so this replacement now silently does nothing. %s"
                % (old, new, paths, _FIX_HINT),
            )

    def test_allowlist_covers_every_odoo_wordmark_in_core(self):
        """The allowlist must account for ALL "Odoo" occurrences, not just
        the ones it happens to know.

        Catches rot mode 2 (core added a NEW wordmark): counts every raw
        "Odoo" in the concatenated template source and requires the allowlist
        to account for exactly that many. A newly added wordmark makes the
        count exceed the coverage and fails loudly here, instead of leaking
        onto the pre-auth page.

        Every allowlist ``old`` contains exactly one "Odoo", and no two
        entries overlap in the source, so coverage is simply the number of
        matches each entry has.
        """
        source, paths = self._core_template_source()
        total = source.count(_WORDMARK_TOKEN)
        per_entry = {old: source.count(old) for old, _new in _WORDMARK_STRINGS}
        covered = sum(per_entry.values())
        self.assertEqual(
            covered, total,
            "the de-brand allowlist covers %d of the %d %r occurrences in the "
            "core templates %s.\nPer-entry match counts: %s\nA core update "
            "added a wordmark the allowlist does not know about; it will ship "
            "un-de-branded on /web/database/manager. %s"
            % (covered, total, _WORDMARK_TOKEN, paths, per_entry, _FIX_HINT),
        )

    def test_odoo_com_links_are_all_covered(self):
        """Every ``odoo.com`` link in the templates must be de-branded too.

        The lowercase-"odoo" exclusion above is about ROUTES and ASSET paths,
        which must not be touched. A ``odoo.com`` URL is neither - it is
        branding, and an un-rewritten one sends a pre-auth visitor to Odoo.
        Today that is exactly the one privacy-policy link the asset allowlist
        replaces; a second one appearing must fail here.
        """
        source, paths = self._core_template_source()
        total = source.count('odoo.com')
        # Count coverage by FREQUENCY, not membership: `old.count('odoo.com')`
        # is a frequency multiplier (0 for non-odoo.com entries, >=1 otherwise),
        # not a boolean URL guard - so it also credits an entry that rewrites
        # more than one odoo.com link, and it does not trip CodeQL's
        # `py/incomplete-url-substring-sanitization` heuristic (which flags a bare
        # `'odoo.com' in <var>` as if it were validating an untrusted URL). This
        # is a source-scan assertion over fixed de-brand literals, not runtime
        # URL sanitization of any input.
        covered = sum(
            source.count(old) * old.count('odoo.com') for old, _new in _ASSET_STRINGS
        )
        self.assertEqual(
            covered, total,
            "the asset allowlist covers %d of the %d 'odoo.com' links in the "
            "core templates %s - a core update added an odoo.com link that "
            "will not be de-branded. %s" % (covered, total, paths, _FIX_HINT),
        )

    def test_logo_class_rewrite_target_is_unique(self):
        """The cosmetic Bootstrap-class rewrite must match exactly one place.

        ``('img-fluid d-block mx-auto', 'img-fluid d-block mx-auto my-4')`` is
        an unscoped class-trio rewrite: it is safe only while that trio is
        unique to the logo ``<img>``. If core ever applies the same trio to
        another element, the extra vertical margin lands there too. Scoping
        the replacement structurally is not an option (the response is
        lxml-re-serialised, so a full-tag literal could silently no-op - see
        the rationale in controllers/database.py), so uniqueness is asserted
        here instead.
        """
        source, paths = self._core_template_source()
        target = 'img-fluid d-block mx-auto'
        self.assertEqual(
            source.count(target), 1,
            "%r occurs %d times in the core templates %s - the de-brand "
            "applies an unscoped class rewrite to it, which is only safe "
            "while it is unique to the logo <img>. Scope the replacement (or "
            "drop the cosmetic margin) before this ships. %s"
            % (target, source.count(target), paths, _FIX_HINT),
        )
