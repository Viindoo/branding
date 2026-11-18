import inspect
import re

from odoo.tests.common import BaseCase, tagged
from odoo.tools.misc import file_open

from odoo.addons.web.controllers.database import Database as CoreDatabase
from ..controllers.database import _ASSET_STRINGS, _WORDMARK_STRINGS

# Case-sensitive: the wordmark is the capitalised brand token. Lowercase "odoo" is structural
# (the login route ``/odoo?db={{ db }}``, the core asset paths) and must survive de-brand. The
# one lowercase branding site, the ``www.odoo.com`` privacy link, is covered by
# ``test_odoo_com_links_are_all_covered``.
_WORDMARK_TOKEN = 'Odoo'

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
    positive allowlist of fixed literal strings (a blanket "Odoo" -> "Viindoo"
    replace corrupts database NAMES - see test_database_manager_dbname_safety.py).
    An allowlist silently rots in two ways, both leaving an Odoo wordmark on a
    pre-auth page:

    1. Core REWORDS an existing string -> the ``old`` literal stops matching.
    2. Core ADDS a new "Odoo" occurrence -> the allowlist never knew about it.

    The HTTP tests assert on the strings the allowlist already knows, so they
    cannot catch either. This test is fully static: it reads the core templates
    with ``file_open`` and compares them against the allowlist tuples imported
    from the controller.
    """

    @classmethod
    def _core_template_paths(cls):
        """Return the template paths CORE's ``_render_template`` actually loads.

        Read out of core's own source, so a template core adds widens this test's
        scope automatically.
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

        If core stops loading templates this way, the regex returns an empty list
        and every downstream assertion would pass vacuously.
        """
        paths = self._core_template_paths()
        self.assertTrue(
            paths,
            "could not discover any *.qweb.html template in the source of "
            "odoo.addons.web.controllers.database.Database._render_template - "
            "core changed how it loads the database-manager templates, so the "
            "de-brand allowlist cannot be verified against them. "
            + _FIX_HINT,
        )
        for path in paths:
            self.assertTrue(
                self._read(path),
                "core template %s is empty or unreadable" % path,
            )

    def test_every_allowlist_target_still_exists_in_core(self):
        """Every ``old`` literal the override replaces must exist on disk.

        A missing ``old`` means that replacement no-ops in production and the
        corresponding Odoo string ships un-de-branded.
        """
        source, paths = self._core_template_source()
        for old, new in _WORDMARK_STRINGS + _ASSET_STRINGS:
            self.assertIn(
                old, source,
                "the de-brand allowlist entry %r -> %r does not match "
                "anything in the core templates %s. Core reworded or removed "
                "it, so this replacement now silently does nothing. %s"
                % (old, new, paths, _FIX_HINT),
            )

    def test_allowlist_covers_every_odoo_wordmark_in_core(self):
        """The allowlist must account for ALL "Odoo" occurrences, not just
        the ones it happens to know.

        Counts every raw "Odoo" in the concatenated template source and requires
        the allowlist to account for exactly that many.

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

        Routes and asset paths containing lowercase "odoo" must not be touched; an
        ``odoo.com`` URL is branding, and an un-rewritten one sends a pre-auth
        visitor to Odoo. The asset allowlist replaces the privacy-policy link; a
        second ``odoo.com`` link must fail here.
        """
        source, paths = self._core_template_source()
        total = source.count('odoo.com')
        # Coverage by frequency: `old.count('odoo.com')` multiplies (0 for entries without
        # an odoo.com link) rather than testing membership, which would trip CodeQL's
        # `py/incomplete-url-substring-sanitization`; this scans fixed literals, it
        # sanitizes no URL.
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
        unique to the logo ``<img>``; otherwise the extra vertical margin lands
        on another element too. The response is lxml-re-serialised, so a
        full-tag literal could silently no-op and uniqueness is asserted instead.
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
