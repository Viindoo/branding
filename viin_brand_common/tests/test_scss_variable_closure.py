# Sass variable CLOSURE guard (ODOO-AI-ETHOS #8) - protects the business rule:
#
#   "Every Sass variable this repo's own SCSS READS must be DEFINED somewhere that is actually
#    reachable in EACH asset bundle that consumes it."
#
# When that rule breaks the consequence is not cosmetic: Dart Sass aborts the whole bundle with
# `Error: Undefined variable`, the bundle serves no CSS, and the entire backend/frontend UI is
# dead. This guard was written for a live production break on 19.0 where three of Odoo's main
# bundles failed to compile at once:
#     web.assets_backend   -> Undefined variable: "$brand-primary-light"
#     web.assets_frontend  -> Undefined variable: "$brand-primary"
#     web.assets_web_dark  -> Undefined variable: "$brand-primary-light"
# while point_of_sale._assets_pos compiled CLEAN, because viin_brand_pos defines the legacy
# `$brand-*` names in pos_variables.scss - a file contributed ONLY to the POS bundle. The names
# are therefore reachable in POS and unreachable everywhere else: the defect is per-BUNDLE
# reachability, not "is this name defined anywhere in the tree".
#
# WHY THIS IS AN ANALYSIS AND NOT A CHECKLIST OF THE OBSERVED SYMPTOMS
# -------------------------------------------------------------------
# Sass aborts at the FIRST undefined variable, so the compiler error list is always a strict
# UNDER-count. The live errors above named two variables; the source actually reads FIVE
# unreachable ones in the backend bundle - the rest were masked behind the line-2 failure. A
# guard seeded from the observed error list would go green while onboarding.scss was still
# broken, which is worse than no guard at all. So this file never hardcodes the failing names:
# it rebuilds a per-bundle reachability model from source (manifest `assets` blocks + the SCSS
# files themselves) and lets the undefined set FALL OUT of that model.
#
# THE PARSER TRAP THIS GUARD MUST NOT FALL INTO
# ---------------------------------------------
# This repo's SCSS carries very long prose comment headers that mention variable names in
# English (brand_variables.scss's COLOUR LAW block, pos_variables.scss's header, mail_dark.scss).
# Counting a name inside a comment as a DEFINITION is exactly the mistake that let this bug
# ship - it makes every broken name look defined. `_strip_scss_comments` therefore blanks `//`
# and `/* */` regions BEFORE any scanning, and test_scss_comment_prose_is_never_a_definition
# below pins that behaviour so it cannot silently regress.
#
# DELIBERATE SCOPE LIMITS (stated so the next engineer does not mistake them for bugs)
# -----------------------------------------------------------------------------------
# 1. NAMESPACE. Assertions are restricted to the brand-token namespaces this repo owns:
#    `$brand-*` (always) and `$o-*` (only when an Odoo core checkout is resolvable). Modelling
#    every Bootstrap/core variable from source alone is not possible - core declares thousands
#    of names across conditional and generated files - and a whole-namespace closure check would
#    be a false-positive machine. Scoping to the brand namespace keeps the guard deterministic.
# 2. PRESENCE, NOT ORDER. Sass is order-sensitive (a file must be compiled AFTER the file that
#    defines what it reads). This guard asserts PRESENCE in the bundle, not ordering. Ordering
#    is a separate contract and is intentionally NOT modelled here.
# 3. `$o-*` SOUNDNESS GATE. Core's `$o-*` SSOT lives in `web._assets_primary_variables`. A
#    bundle that does not transitively include that bundle resolves `$o-*` through some
#    mechanism this static model cannot see (im_livechat's embed bundles are the live example -
#    38 of CORE's OWN files there read `$o-*` names that are absent from the bundle, which proves
#    the model, not core, is incomplete for that shape). The `$o-*` arm therefore judges only
#    bundles that pull in that SSOT, and additionally never blames this repo for a name that
#    core itself reads unresolved in the same bundle (core as a per-name control group). Both
#    gates are structural, not an allow-list, so they keep working if core restructures.
# 4. The `$brand-*` arm needs NO core checkout and ALWAYS runs: `$brand-*` is a legacy Viindoo
#    namespace that core never defines and never reads (verified: zero occurrences in 19.0
#    core SCSS), so every `$brand-*` name read here must be defined by THIS repo.
#
# Everything is read from disk - no live instance, no bundle compile, no _get_asset_bundle.
import ast
import glob
import os
import re

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
REPO_ROOT = os.path.dirname(MODULE_DIR)
BRAND_VARIABLES_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "brand_variables.scss")

# Namespaces this repo owns and therefore may assert closure over (see scope limit 1).
BRAND_NAMESPACE = ("brand-",)
ODOO_NAMESPACE = ("o-",)

# The bundle that carries core's `$o-*` SSOT; the `$o-*` arm only judges bundles reaching it.
CORE_PRIMARY_VARIABLES_BUNDLE = "web._assets_primary_variables"

# Core bundle-inclusion facts, needed so every arm still runs with NO core checkout present.
# Each edge is transcribed from odoo/addons/web/__manifest__.py and
# odoo/addons/point_of_sale/__manifest__.py on 19.0 and is a LOWER BOUND on core's real include
# set - enough to carry variables into the bundles this repo feeds, not an exhaustive mirror.
# test_documented_core_bundle_includes_still_match_core re-verifies every edge against the real
# core manifests whenever a checkout is resolvable, so this constant cannot rot unnoticed.
CORE_BUNDLE_INCLUDES = {
    # web/__manifest__.py:261 - the primary-variables SSOT enters through the shared helpers.
    "web._assets_helpers": ("web._assets_primary_variables", "web._assets_secondary_variables"),
    "web.assets_backend": (
        "web._assets_helpers",
        "web._assets_backend_helpers",
        "web._assets_bootstrap_backend",
        "web._assets_core",
    ),
    "web.assets_frontend": (
        "web._assets_helpers",
        "web._assets_frontend_helpers",
        "web._assets_bootstrap_frontend",
    ),
    # web/__manifest__.py:147 - assets_web is the backend bundle plus the webclient entrypoints.
    "web.assets_web": ("web.assets_backend",),
    # web/__manifest__.py:346-347 - the dark bundle is an independent RECOMPILE of the light
    # backend bundle, so it sees the same contributions plus the *.dark.scss overlay.
    "web.assets_web_dark": ("web.assets_web",),
    "point_of_sale._assets_pos": ("point_of_sale.base_app", "point_of_sale.base_tests"),
}

_VAR_TOKEN = re.compile(r"\$([A-Za-z_][A-Za-z0-9_-]*)")
_STATEMENT_BOUNDARY = frozenset(";{}")
# Sass constructs that bind a variable LOCALLY - their names are definitions, not reads.
_MIXIN_PARAMS = re.compile(r"@(?:mixin|function)\s+[\w-]+\s*\(([^)]*)\)", re.DOTALL)
_EACH_VARS = re.compile(r"@each\s+(.*?)\s+in\s", re.DOTALL)
_FOR_VAR = re.compile(r"@for\s+(\$[A-Za-z_][A-Za-z0-9_-]*)\s+from\s")


def _strip_scss_comments(source):
    """Blank every `//` and `/* */` region, PRESERVING byte offsets and line breaks.

    Offsets are preserved (comment bytes become spaces, newlines survive) so a match offset in
    the returned text still maps to the right line in the original file. Quote-aware, so a `//`
    inside a quoted string (a url(), a content: value) is NOT treated as a comment.
    """
    out = list(source)
    index, length = 0, len(source)
    quote = None
    while index < length:
        char = source[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        if char == "/" and index + 1 < length and source[index + 1] == "*":
            end = source.find("*/", index + 2)
            end = length if end == -1 else end + 2
            for position in range(index, end):
                if out[position] != "\n":
                    out[position] = " "
            index = end
            continue
        if char == "/" and index + 1 < length and source[index + 1] == "/":
            end = source.find("\n", index)
            end = length if end == -1 else end
            for position in range(index, end):
                out[position] = " "
            index = end
            continue
        index += 1
    return "".join(out)


def _locally_bound_names(stripped):
    """Names bound by @mixin/@function params and @each/@for headers (definitions, not reads)."""
    names = set()
    for group in _MIXIN_PARAMS.findall(stripped):
        names.update(_VAR_TOKEN.findall(group))
    for group in _EACH_VARS.findall(stripped):
        names.update(_VAR_TOKEN.findall(group))
    names.update(match.lstrip("$") for match in _FOR_VAR.findall(stripped))
    return names


def _scan_scss(path):
    """Return (defined_names, {read_name: [line, ...]}) for one SCSS file.

    A token is a DEFINITION when it sits at statement-start position and is immediately followed
    by `:` - i.e. `$name: value`. Everything else that resolves a `$name` is a READ, including
    interpolated `#{$name}` uses. Comments are blanked first (see the parser-trap note above).
    """
    with open(path, "r", encoding="utf-8") as scss_file:
        stripped = _strip_scss_comments(scss_file.read())

    defines = _locally_bound_names(stripped)
    candidates = []
    for match in _VAR_TOKEN.finditer(stripped):
        after = match.end()
        while after < len(stripped) and stripped[after].isspace():
            after += 1
        before = match.start() - 1
        while before >= 0 and stripped[before].isspace():
            before -= 1
        at_statement_start = before < 0 or stripped[before] in _STATEMENT_BOUNDARY
        assigns = after < len(stripped) and stripped[after] == ":"
        if at_statement_start and assigns:
            defines.add(match.group(1))
        else:
            candidates.append(match)

    reads = {}
    for match in candidates:
        name = match.group(1)
        if name in defines:
            continue
        reads.setdefault(name, []).append(stripped.count("\n", 0, match.start()) + 1)
    return defines, reads


def _load_manifest(path):
    """Same literal_eval idiom as tests/test_asset_upgrade.py::_load_manifest."""
    with open(path, "r", encoding="utf-8") as manifest_file:
        return ast.literal_eval(manifest_file.read())


def _resolve_asset_op(op):
    """Classify ONE `assets` entry as ('include', bundle) | ('source', token) | None.

    Deliberately NOT tests/test_asset_upgrade.py::_iter_asset_tokens: that helper flattens EVERY
    string in a tuple, which is right for its retirement check but wrong here - in
    ('after', anchor, source) the ANCHOR names a file this module does not contribute, and
    counting it as a contributed source would inject foreign definitions into the model and hide
    real breaks. Only the true source slot is returned, and 'remove' ops contribute nothing.
    """
    if isinstance(op, str):
        return ("source", op)
    if isinstance(op, (tuple, list)):
        parts = [part for part in op if isinstance(part, str)]
        if not parts:
            return None
        directive = parts[0]
        if directive == "include":
            return ("include", parts[1]) if len(parts) > 1 else None
        if directive == "remove":
            return None
        if len(parts) >= 3:
            return ("source", parts[2])
        if len(parts) == 2:
            return ("source", parts[1])
    return None


def _expand_scss(addons_root, token):
    """Resolve one asset token to the SCSS files on disk it contributes (globs included)."""
    relative = token.lstrip("/")
    if not relative.endswith(".scss") and "*" not in relative:
        return []
    matches = glob.glob(os.path.join(addons_root, relative), recursive=True)
    return sorted(path for path in matches if path.endswith(".scss") and os.path.isfile(path))


def _collect_bundles(addons_roots):
    """Build {bundle: {'sources': [abs scss], 'includes': [bundle]}} from every manifest found."""
    bundles = {}
    for addons_root in addons_roots:
        pattern = os.path.join(addons_root, "*", "__manifest__.py")
        for manifest_path in sorted(glob.glob(pattern)):
            try:
                manifest = _load_manifest(manifest_path)
            except (SyntaxError, ValueError):
                continue
            if not isinstance(manifest, dict):
                continue
            for bundle, ops in (manifest.get("assets") or {}).items():
                entry = bundles.setdefault(bundle, {"sources": [], "includes": []})
                for op in ops:
                    resolved = _resolve_asset_op(op)
                    if not resolved:
                        continue
                    kind, value = resolved
                    if kind == "include":
                        entry["includes"].append(value)
                    else:
                        entry["sources"].extend(_expand_scss(addons_root, value))
    return bundles


def _bundle_closure(bundle, bundles):
    """Every bundle whose files land in `bundle`, following include edges transitively.

    Include edges come from the manifests actually on disk PLUS the documented CORE_BUNDLE_INCLUDES
    lower bound, so the closure stays correct with no core checkout present.
    """
    seen, stack = set(), [bundle]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(bundles.get(current, {}).get("includes", ()))
        stack.extend(CORE_BUNDLE_INCLUDES.get(current, ()))
    return seen


def _core_addons_roots():
    """Resolve Odoo core addons roots portably, or return () when none is available.

    Env override first (ODOO_SOURCE_PATH / ODOO_CORE_PATH, pointing at a checkout), otherwise the
    core actually running this test - which is by definition the right one. Never a machine path.
    """
    checkout = os.environ.get("ODOO_SOURCE_PATH") or os.environ.get("ODOO_CORE_PATH")
    if not checkout:
        try:
            import odoo as odoo_package
        except ImportError:
            return ()
        package_file = getattr(odoo_package, "__file__", None)
        if not package_file:
            return ()
        checkout = os.path.dirname(os.path.dirname(os.path.abspath(package_file)))
    roots = []
    for relative in ("addons", os.path.join("odoo", "addons")):
        root = os.path.join(checkout, relative)
        if os.path.isdir(root):
            roots.append(root)
    return tuple(roots)


def _unreachable_variables(repo_root, prefixes, core_roots=(), require_bundle=None):
    """Per-bundle closure analysis. Returns {bundle: {name: [(relpath, line), ...]}}.

    A name is reported for a bundle when this repo's SCSS in that bundle READS it, the name is in
    one of `prefixes`, and NO file reachable in that bundle DEFINES it. Two soundness gates apply
    (see scope limit 3): `require_bundle` restricts the analysis to bundles that transitively
    include the bundle carrying the namespace's SSOT, and any name that CORE's own files also read
    unresolved in the same bundle is suppressed - core is the control group for what this static
    model can explain, so the repo is never blamed for a gap the model cannot see.
    """
    repo_bundles = _collect_bundles([repo_root])
    core_bundles = _collect_bundles(core_roots) if core_roots else {}

    merged = {}
    for source in (core_bundles, repo_bundles):
        for bundle, entry in source.items():
            target = merged.setdefault(bundle, {"sources": [], "includes": []})
            target["sources"].extend(entry["sources"])
            target["includes"].extend(entry["includes"])

    scanned = {}

    def scan(path):
        if path not in scanned:
            scanned[path] = _scan_scss(path)
        return scanned[path]

    findings = {}
    for bundle, entry in sorted(repo_bundles.items()):
        if not entry["sources"]:
            continue
        family = _bundle_closure(bundle, merged)
        if require_bundle and require_bundle not in family:
            continue
        repo_files, core_files = set(), set()
        for member in family:
            repo_files.update(repo_bundles.get(member, {}).get("sources", ()))
            core_files.update(core_bundles.get(member, {}).get("sources", ()))

        defined = set()
        for path in repo_files | core_files:
            defined |= scan(path)[0]

        core_unexplained = set()
        for path in core_files:
            core_unexplained |= {name for name in scan(path)[1] if name not in defined}

        unreachable = {}
        for path in sorted(repo_files):
            for name, lines in scan(path)[1].items():
                if name in defined or name in core_unexplained:
                    continue
                if not name.startswith(prefixes):
                    continue
                relative = os.path.relpath(path, repo_root)
                unreachable.setdefault(name, []).extend((relative, line) for line in lines)
        if unreachable:
            findings[bundle] = unreachable
    return findings


def _format_findings(findings):
    lines = []
    for bundle in sorted(findings):
        lines.append("  bundle %s:" % bundle)
        for name in sorted(findings[bundle]):
            sites = ", ".join(
                "%s:%d" % (path, line) for path, line in sorted(set(findings[bundle][name]))
            )
            lines.append("      $%s  read at %s" % (name, sites))
    return "\n".join(lines)


@tagged("post_install", "-at_install")
class ScssVariableClosureTest(TransactionCase):

    def test_every_brand_variable_read_is_defined_in_the_bundle_that_reads_it(self):
        """A `$brand-*` name this repo READS must be DEFINED in EVERY bundle that consumes it.

        The bundle - not the repo - is the unit of reachability: defining a name in a file that
        only reaches point_of_sale._assets_pos leaves every other bundle broken. This arm needs no
        Odoo core checkout, because `$brand-*` is a legacy Viindoo namespace core neither defines
        nor reads, so every such name must be satisfied from inside this repo.
        """
        findings = _unreachable_variables(
            REPO_ROOT, BRAND_NAMESPACE, core_roots=_core_addons_roots()
        )
        self.assertFalse(
            findings,
            "Sass will abort these bundles with `Undefined variable` and serve NO CSS, killing "
            "the whole UI they style:\n%s\n\n"
            "Fix by DEFINING each name somewhere reachable in the failing bundle - e.g. a "
            "variables file contributed to web._assets_primary_variables (which core includes "
            "into both web.assets_backend and web.assets_frontend), or by rewriting the reader "
            "onto a token that already exists there. Do NOT fix this by defining only the names "
            "listed in a compiler error log: Sass stops at the FIRST undefined variable, so that "
            "list is always shorter than the real set - this guard reports ALL of them."
            % _format_findings(findings),
        )

    def test_every_odoo_namespace_variable_read_is_defined_in_the_bundle_that_reads_it(self):
        """Same closure rule for the `$o-*` tokens this repo reads, where core can be consulted.

        Skips cleanly when no Odoo core checkout is resolvable: core owns most `$o-*` declarations,
        so without it every read would look undefined. Bundles that do not pull in core's
        `$o-*` SSOT bundle are also skipped - see scope limit 3.
        """
        core_roots = _core_addons_roots()
        if not core_roots:
            self.skipTest(
                "no Odoo core checkout resolvable (set ODOO_SOURCE_PATH to a checkout); the $o-* "
                "arm needs core's declarations, while the $brand-* arm above always runs"
            )
        findings = _unreachable_variables(
            REPO_ROOT,
            ODOO_NAMESPACE,
            core_roots=core_roots,
            require_bundle=CORE_PRIMARY_VARIABLES_BUNDLE,
        )
        self.assertFalse(
            findings,
            "These `$o-*` reads resolve to nothing in the bundle that consumes them, which aborts "
            "the bundle with `Undefined variable`:\n%s\n\n"
            "Fix by contributing a definition into that bundle, or by reading a token core "
            "actually declares there." % _format_findings(findings),
        )

    def test_scss_comment_prose_is_never_a_definition(self):
        """A variable NAMED IN A COMMENT must count as neither a definition nor a read.

        This pins the parser behaviour the whole guard rests on. This repo's SCSS carries long
        prose headers that name variables in English; if comment text counted as a definition,
        every broken name would look satisfied and both arms above would go green while the
        bundles stayed dead - which is precisely how the live break shipped.
        """
        fixture = (
            "// $brand-commented-line is only discussed here\n"
            "/* $brand-commented-block is only discussed here\n"
            "   $brand-commented-more too */\n"
            "$brand-real-definition: #00BBCE;\n"
            ".x { color: $brand-real-read; }\n"
        )
        stripped = _strip_scss_comments(fixture)
        self.assertEqual(
            stripped.count("\n"), fixture.count("\n"),
            "comment stripping must PRESERVE line breaks, else reported file:line is wrong",
        )
        for prose_only in ("brand-commented-line", "brand-commented-block", "brand-commented-more"):
            self.assertNotIn("$" + prose_only, stripped, "comment text must be blanked")

        # Same contract against real repo source: brand_variables.scss discusses the legacy
        # `$brand-primary-dark` / `$brand-primary-darker` names in its COLOUR LAW prose but must
        # not be credited with defining or reading them.
        self.assertTrue(
            os.path.exists(BRAND_VARIABLES_SCSS),
            "brand_variables.scss must exist at %s" % BRAND_VARIABLES_SCSS,
        )
        defines, reads = _scan_scss(BRAND_VARIABLES_SCSS)
        for prose_only in ("brand-primary-dark", "brand-primary-darker"):
            self.assertNotIn(
                prose_only, defines,
                "$%s is only PROSE in brand_variables.scss - counting it as a definition would "
                "mask a real undefined-variable break in every bundle that reads it" % prose_only,
            )
            self.assertNotIn(
                prose_only, reads,
                "$%s is only PROSE in brand_variables.scss - counting it as a read would raise a "
                "false break against a file that never resolves it" % prose_only,
            )

    def test_documented_core_bundle_includes_still_match_core(self):
        """Every documented core include edge must still exist in the real core manifests.

        CORE_BUNDLE_INCLUDES is what keeps the arms above correct with no core checkout present
        (notably web.assets_web_dark -> web.assets_web -> web.assets_backend, without which the
        dark bundle would appear to contain nothing and its break would go unreported). A stale
        constant would silently shrink the model, so it is re-verified whenever core is resolvable.
        """
        core_roots = _core_addons_roots()
        if not core_roots:
            self.skipTest("no Odoo core checkout resolvable to verify CORE_BUNDLE_INCLUDES against")
        core_bundles = _collect_bundles(core_roots)
        for bundle, documented in sorted(CORE_BUNDLE_INCLUDES.items()):
            actual = core_bundles.get(bundle, {}).get("includes", [])
            self.assertTrue(
                actual,
                "CORE_BUNDLE_INCLUDES documents %r but core declares no includes for it - the "
                "bundle was renamed or restructured; re-derive the constant from core." % bundle,
            )
            for included in documented:
                self.assertIn(
                    included, actual,
                    "CORE_BUNDLE_INCLUDES claims %r includes %r but core no longer does. The "
                    "closure model is now wrong for that bundle - re-derive this constant from "
                    "the core manifest before trusting the arms above." % (bundle, included),
                )
