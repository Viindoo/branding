# Copyright 2026 Viindoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import ast
import os

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

# `viin_brand` is the repo's foundation module (auto_install, depends on
# `base` only, category "Hidden") and is present on every DB in this
# branding suite regardless of which vertical modules are installed
# alongside it, so this repo-wide filesystem guard is hosted here even
# though the modules it inspects carry no dependency edge to `viin_brand`
# itself. Resolved relative to THIS file, never hardcoded, so the guard
# keeps working from any checkout/worktree of this repo:
#   <repo_root>/viin_brand/tests/test_manifest_assets_no_set_literals.py
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _iter_top_level_manifest_paths(repo_root):
    """Yield the ``__manifest__.py`` path of every top-level addon under ``repo_root``."""
    for entry in sorted(os.listdir(repo_root)):
        manifest_path = os.path.join(repo_root, entry, "__manifest__.py")
        if os.path.isfile(manifest_path):
            yield manifest_path


def _load_manifest_dict(manifest_path):
    """Parse a manifest file into a plain Python object graph via ``ast.literal_eval``.

    Never ``import``s the file: manifests are data, not code meant to run, and
    importing 56 of them would execute whatever each one's top-level
    statements happen to do. Never regex/brace-counts either: a regex
    misfires on an empty dict (``{}``), on a string literal that happens to
    contain braces, and on a commented-out example manifest snippet - all
    real shapes a manifest can take. ``ast.parse`` ignores comments by
    construction and never looks inside string contents, so none of those
    misfire here. Using ``ast.literal_eval`` on the manifest's own outer
    ``Dict`` node (rather than re-implementing the walk key by key) is also
    what makes the type distinction free: a `set` literal in the source
    evaluates to a Python ``set``, a `dict` literal to a ``dict``, and a
    `list`/`tuple` literal to a ``list``/``tuple`` - exactly the distinction
    this guard needs, with no extra bookkeeping.
    """
    with open(manifest_path, "r", encoding="utf-8") as manifest_file:
        source = manifest_file.read()
    tree = ast.parse(source, filename=manifest_path)
    manifest_node = next(node for node in ast.walk(tree) if isinstance(node, ast.Dict))
    return ast.literal_eval(manifest_node)


@tagged("-at_install", "post_install")
class TestManifestAssetsNoSetLiterals(TransactionCase):
    """No manifest in this repo may declare an `assets` bundle as a Python `set` literal.

    An assets bundle's value is the ORDERED list of files Odoo concatenates
    into that bundle. CPython randomizes string hashing per process
    (``PYTHONHASHSEED``), so iterating a ``set`` yields a different element
    order every time the Odoo server process starts - a `set` literal there
    makes the file LOAD ORDER inside that bundle nondeterministic across
    deployments/restarts. That is harmless only by accident: the moment two
    files in the same set-literal bundle define an overlapping rule (an SCSS
    variable, for instance), whichever one "wins" flips randomly between
    server restarts - a bug class that cannot be reliably reproduced.

    This test never touches the ORM or any other module's registry - it
    parses every top-level addon's ``__manifest__.py`` directly off disk, so
    it needs no other module installed to see them.
    """

    def test_no_manifest_declares_an_assets_bundle_as_a_set_literal(self):
        offenders = []
        for manifest_path in _iter_top_level_manifest_paths(REPO_ROOT):
            module_name = os.path.basename(os.path.dirname(manifest_path))
            manifest = _load_manifest_dict(manifest_path)
            assets = manifest.get("assets") or {}
            for bundle_name, bundle_value in assets.items():
                if isinstance(bundle_value, (set, frozenset)):
                    offenders.append("%s:%s" % (module_name, bundle_name))
        self.assertFalse(
            offenders,
            "The following <module>:<bundle> pairs declare their `assets` "
            "bundle as a Python `set` literal instead of a `list`/`tuple`: "
            "%s. CPython randomizes string hashing per process "
            "(PYTHONHASHSEED), so a `set` iterates in a different order "
            "every time the Odoo server starts - that makes the LOAD ORDER "
            "of the files inside that bundle nondeterministic across "
            "deployments/restarts. It is harmless only for as long as no "
            "two files in the bundle define an overlapping rule (an SCSS "
            "variable, for instance); the moment they do, whichever one "
            "\"wins\" will flip randomly between restarts - a bug class "
            "that cannot be reliably reproduced. Fix: change the bundle's "
            "value from a `set` literal (`{...}`) to a `list` (`[...]`)."
            % ", ".join(offenders),
        )

    def test_manifest_scan_covers_a_realistic_slice_of_the_repo(self):
        """`assertFalse(offenders, ...)` above cannot tell "scanned everything,
        found zero violations" apart from "scanned nothing at all" - a wrong
        `REPO_ROOT` after a repo move, a changed checkout layout, or a
        silently-broken `os.listdir`/glob call would all leave `offenders`
        empty and make the sibling test PASS for the wrong reason. This test
        protects that: it asserts the scan itself actually walked a
        realistic slice of the repo, so a "0 offenders" verdict from the
        sibling test is provably backed by a real scan, not a silent no-op.
        """
        manifest_paths = list(_iter_top_level_manifest_paths(REPO_ROOT))
        self.assertGreaterEqual(
            len(manifest_paths),
            40,
            "The manifest scan under REPO_ROOT=%s found only %d top-level "
            "__manifest__.py file(s) - below the required floor of 40. This "
            "means the manifest scanner DID NOT RUN (or ran over almost "
            "nothing) - it does NOT mean there are no set-literal `assets` "
            "bundles; that is "
            "test_no_manifest_declares_an_assets_bundle_as_a_set_literal's "
            "job, not this test's. This repo currently has 56 top-level "
            "__manifest__.py files; 40 leaves about 16 modules (~29%%) of "
            "headroom below that count - enough to absorb ordinary future "
            "module add/remove churn without false-redding on a routine "
            "change, while still catching a total scan collapse (0), a "
            "badly-wrong REPO_ROOT (e.g. resolving one level too deep, "
            "landing inside a single module's own directory), or a "
            "glob/listdir call that silently stops matching most of the "
            "tree. If this fails, fix the scan (REPO_ROOT resolution / "
            "checkout layout) before trusting the sibling test's result."
            % (REPO_ROOT, len(manifest_paths)),
        )
