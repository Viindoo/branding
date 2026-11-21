# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Regression guard for a Hoot API-misuse bug class: `describe.tags(...)` / `test.tags(...)` are
# the BUFFERED form - they stash tags for the NEXT `describe()` call, not the current suite (Odoo
# 19.0 Hoot `addons/web/static/lib/hoot/core/runner.js`). A normal Odoo `.test.js` file never calls
# `describe()` itself - its top-level suite is created for it by `module_set.hoot.js` - so a stray
# `describe.tags(...)` silently leaks its tags onto whichever file's suite loads NEXT. The correct
# call is `describe.current.tags(...)`, which tags the CURRENT suite directly.
#
# A leaked `desktop` tag combined with a `headless` tag on the next suite violates Hoot's
# mutually-exclusive desktop/mobile/headless tag rule (`start.hoot.js`, `tag.js`) and aborts the
# whole Hoot run.
import glob
import os
import re

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)

# Matches ONLY the buffered form `describe.tags(` / `test.tags(` at the start of a line; the
# correct `describe.current.tags(` form spells `current.tags(` and never lines up. The `^\s*`
# anchor also excludes mentions inside `//` comment lines.
BUFFERED_TAGS_CALL_RE = re.compile(r"^\s*(?:describe|test)\.tags\(")

EXPLANATION = (
    "describe.tags(...) / test.tags(...) is the BUFFERED Hoot form: it stashes tags for the NEXT "
    "describe() call, not the current suite. A normal Odoo .test.js file never calls describe() "
    "itself - its suite is created for it by module_set.hoot.js - so a stray "
    "describe.tags(...)/test.tags(...) call silently leaks its tags onto whichever suite loads "
    "NEXT instead of tagging itself. Use describe.current.tags(...) / test.current.tags(...) to "
    "tag the CURRENT suite. A leaked \"desktop\" tag combined with a \"headless\" tag on the next "
    "suite hits Hoot's mutually-exclusive desktop/mobile/headless rule and aborts the entire "
    "Hoot run."
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
