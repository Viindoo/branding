# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Regression guard for a proven Hoot API-misuse bug class (ODOO-AI-ETHOS #8: protect the
# BEHAVIOR/contract, not a snapshot of today's code): `describe.tags(...)` / `test.tags(...)` are
# the BUFFERED form - they stash tags for the NEXT `describe()` call, not the current suite (Odoo
# 19.0 Hoot `addons/web/static/lib/hoot/core/runner.js:1304`, drained at `runner.js:1316-1319` when
# the NEXT `describe()` runs). A normal Odoo `.test.js` file never calls `describe()` itself - its
# top-level suite is created FOR it by `module_set.hoot.js:108` - so a stray `describe.tags(...)`
# in one file silently leaks its tags onto whichever file's suite loads NEXT, not onto its own
# suite. The correct call is `describe.current.tags(...)` (`runner.js:1411`), which tags the
# CURRENT suite directly. This is already this module's own dominant convention (6 correct
# `describe.current.tags(...)` call sites) - this guard protects that convention going forward.
#
# WHY THIS MATTERS (proven failure, this session): `action_dialog_debrand.test.js` asked for the
# `desktop` tag via the buffered form and got nothing applied to itself; the NEXT suite,
# `documentation_link_debrand.test.js`, inherited the leaked `["desktop"]` tag and then asked for
# `headless` on top of it. Hoot's mutually-exclusive desktop/mobile/headless tag rule
# (`start.hoot.js:29-46`, enforced `tag.js:96-104`) threw on the conflict, aborting the whole Hoot
# dry run before 5 other suites ever executed. A second file, `upgrade_dialog_debrand.test.js`, has
# the SAME bug latently - it leaks onto `error_dialogs_debrand`, which happens to also want
# `desktop`, so nothing throws today, but `upgrade_dialog_debrand` itself has been running UNTAGGED,
# silently wrong.
import glob
import os
import re

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)

# Anchored so it matches ONLY the buffered, wrong form `describe.tags(` / `test.tags(` at the start
# of a line (optionally indented). It must NOT match the correct `describe.current.tags(` /
# `test.current.tags(` forms: after `describe.` (or `test.`) those spell `current.tags(`, not
# `tags(`, so the literal `tags\(` immediately following `describe.` / `test.` never lines up with
# them - no negative lookahead is needed for that distinction. The `^\s*` anchor also excludes any
# mention inside a `//`-prefixed comment line, since `//` never matches `\s*`.
BUFFERED_TAGS_CALL_RE = re.compile(r"^\s*(?:describe|test)\.tags\(")

EXPLANATION = (
    "describe.tags(...) / test.tags(...) is the BUFFERED Hoot form: it stashes tags for the NEXT "
    "describe() call (runner.js:1304, drained at runner.js:1316-1319 by the next describe()), not "
    "the current suite. A normal Odoo .test.js file never calls describe() itself - its suite is "
    "created for it by module_set.hoot.js:108 - so a stray describe.tags(...)/test.tags(...) call "
    "silently leaks its tags onto whichever suite loads NEXT instead of tagging itself. Use "
    "describe.current.tags(...) / test.current.tags(...) (runner.js:1411) to tag the CURRENT suite. "
    "This already leaked once this session: action_dialog_debrand.test.js's buffered "
    "describe.tags(\"desktop\") applied to nothing, then leaked onto documentation_link_debrand."
    "test.js's suite, which then asked for \"headless\" on top of the leaked \"desktop\" tag and "
    "hit Hoot's mutually-exclusive desktop/mobile/headless rule (start.hoot.js:29-46, enforced "
    "tag.js:96-104), aborting the entire Hoot dry run."
)


def _iter_test_js_files():
    pattern = os.path.join(MODULE_DIR, "static", "tests", "**", "*.test.js")
    return sorted(glob.glob(pattern, recursive=True))


@tagged("post_install", "-at_install")
class HootTagBufferGuardTest(TransactionCase):
    """Guard: no `.test.js` file under static/tests may use the buffered `describe.tags(...)` /
    `test.tags(...)` form - only the current-suite `describe.current.tags(...)` / `test.current.
    tags(...)` form is safe to use in a file that does not itself call describe()."""

    def test_no_buffered_describe_or_test_tags_calls(self):
        js_files = _iter_test_js_files()
        self.assertTrue(
            js_files,
            "no *.test.js files found under static/tests/ - the glob pattern or module layout "
            "changed; this guard has nothing to scan.",
        )

        matches = []
        for path in js_files:
            with open(path, "r", encoding="utf-8") as js_file:
                for lineno, line in enumerate(js_file, start=1):
                    if BUFFERED_TAGS_CALL_RE.match(line):
                        matches.append("%s:%d: %s" % (os.path.relpath(path, MODULE_DIR), lineno, line.strip()))

        self.assertEqual(
            len(matches), 0,
            "found %d buffered describe.tags(...)/test.tags(...) call(s), which silently mistag "
            "the WRONG suite instead of the current one:\n%s\n\n%s"
            % (len(matches), "\n".join(matches), EXPLANATION),
        )
