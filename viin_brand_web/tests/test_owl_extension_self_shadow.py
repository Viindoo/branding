# OWL extension self-shadow guard (ODOO-AI-ETHOS #8) - protects the business rule:
#
#   "No OWL/QWeb template in `t-inherit-mode="extension"` may redeclare `t-name` equal to its
#    own `t-inherit` target."
#
# WHY THIS MATTERS
# -----------------
# When `t-name` duplicates `t-inherit` on a `t-inherit-mode="extension"` element, the JS
# template registry treats the extension arch as a REPLACEMENT of the parent template (same
# registry key, last one registered wins) instead of an EXTENSION of it. The xpath edits the
# author wrote silently become a no-op - there is zero load-time error, because the registry key
# still resolves to *something*, just not the extended arch. This exact class has already broken
# this branch's asset bundle twice in its history. Core ships this pattern 0 times across its own
# extension-mode OWL templates on this version: every core template in `t-inherit-mode="extension"`
# either omits `t-name` entirely, or (rarely) uses a genuinely distinct name for a legitimate
# reason - never a self-reference.
#
# CLASS OF BUG GUARDED
# ---------------------
# A silent-shadow defect: the broken template still LOADS, still RENDERS (as the unmodified
# parent), and raises no exception anywhere in the pipeline. It only shows up as "my xpath change
# never took effect", which is easy to misdiagnose as a caching or specificity problem instead of
# what it actually is.
#
# DELIBERATE SCOPE LIMITS
# ------------------------
# 1. SCOPE. Every `*.xml` under any module's `static/src/**` in the WHOLE worktree (repo-wide),
#    not just the module(s) this file happens to live in - the mechanism is JS-registry-wide, so
#    a violation in any module can shadow a template any other module also touches.
# 2. NEVER A HARDCODED FILE LIST. `_static_src_xml_files` / `_self_shadowing_extensions`
#    re-parse the repo from disk on every run - no allow-list, no fixed set of "already known
#    offenders" baked into the traversal. A newly introduced violation anywhere is caught
#    automatically; this file never needs updating in lockstep with new modules.
# 3. `t-inherit-mode="extension"` only. `t-inherit-mode="primary"` (a genuinely new template
#    that happens to extend another for initial content) legitimately needs its own `t-name` and
#    is out of scope - this guard only fires on `extension` mode, where `t-name` is redundant by
#    construction (the target name is already carried by `t-inherit`).
# 4. PARSED WITH REGEX, NOT AN XML TREE PARSER - deliberately, matching the precedent already set
#    in this repo (viin_backend_theme/tests/test_theme_core_chrome_untouched.py::
#    _apps_button_classes): `defusedxml` is not a dependency this codebase carries (core Odoo
#    19.0 itself uses stdlib `xml.etree.ElementTree` for its own internal parsing - see
#    odoo/service/db.py - so this is not a project-wide security posture change, just avoiding an
#    unnecessary new import), and the stdlib tree parsers carry known XXE/entity-expansion
#    exposure that a tag-level regex over trusted, repo-local source files never needs to accept.
#    XML comments are stripped first so a commented-out example is never mistaken for a live tag.
#
# Everything is read from disk - no live instance, no OWL registry, no asset bundle build. A
# TransactionCase whose assertion body never touches self.env is an established pattern in this
# module for pure static/file-parsing guards (see test_scss_variable_closure.py).
import glob
import os
import re
import tempfile

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
REPO_ROOT = os.path.dirname(MODULE_DIR)

EXTENSION_MODE = "extension"

_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_T_TAG_RE = re.compile(r"<t\b([^>]*)>")
_ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def _static_src_xml_files(repo_root):
    """Every *.xml file under any module's static/src/** in the whole worktree."""
    pattern = os.path.join(repo_root, "*", "static", "src", "**", "*.xml")
    return sorted(glob.glob(pattern, recursive=True))


def _line_of(path, needle):
    """Best-effort 1-based line number of the first line containing `needle`, else None.

    This repo's OWL extension templates are consistently single-line (`<t t-name=...
    t-inherit=... t-inherit-mode="extension" ...>`), so a plain substring search is enough for a
    helpful error message; it degrades to `None` (caller falls back to the bare relpath) for any
    template laid out differently instead of reporting a wrong line.
    """
    with open(path, "r", encoding="utf-8") as xml_file:
        for number, line in enumerate(xml_file, start=1):
            if needle in line:
                return number
    return None


def _iter_t_tag_attrs(text):
    """Yield the {attr_name: value} dict for every `<t ...>` tag in comment-stripped text.

    `<t\\b` requires a word boundary right after "t", so it matches `<t `/`<t>` only - it never
    matches the `<templates>` container tag ("t" immediately followed by the word char "e" has
    no boundary there).
    """
    stripped = _XML_COMMENT_RE.sub("", text)
    for match in _T_TAG_RE.finditer(stripped):
        yield dict(_ATTR_RE.findall(match.group(1)))


def _self_shadowing_extensions(paths):
    """Return (violations, total_extension_elements) for the given XML file paths.

    violations: [(path, line_or_None, t_name)] for every t-inherit-mode="extension" element
    whose t-name equals its own t-inherit target.
    total_extension_elements: count of ALL t-inherit-mode="extension" elements scanned
    (violating or not) - lets a caller prove the scan is not vacuously passing because it
    matched zero files (see test_scanner_actually_finds_extension_mode_templates below).
    """
    violations = []
    total_extension_elements = 0
    for path in paths:
        with open(path, "r", encoding="utf-8") as xml_file:
            text = xml_file.read()
        for attrs in _iter_t_tag_attrs(text):
            if attrs.get("t-inherit-mode") != EXTENSION_MODE:
                continue
            total_extension_elements += 1
            t_name = attrs.get("t-name")
            t_inherit = attrs.get("t-inherit")
            if t_name and t_inherit and t_name == t_inherit:
                violations.append((path, _line_of(path, 't-name="%s"' % t_name), t_name))
    return violations, total_extension_elements


def _format_violations(repo_root, violations):
    lines = []
    for path, line, name in sorted(violations):
        relative = os.path.relpath(path, repo_root)
        location = "%s:%d" % (relative, line) if line else relative
        lines.append("  %s  t-name == t-inherit == %r" % (location, name))
    return "\n".join(lines)


@tagged("post_install", "-at_install")
class OwlExtensionSelfShadowTest(TransactionCase):

    def test_no_extension_template_self_shadows_its_inherit_target(self):
        """A t-inherit-mode="extension" template must never redeclare t-name == t-inherit.

        See module header for the full mechanism: a match here means the JS template registry
        will REPLACE the parent template instead of extending it, and the author's xpath edits
        become a silent no-op with zero load-time error.
        """
        paths = _static_src_xml_files(REPO_ROOT)
        violations, _total = _self_shadowing_extensions(paths)
        self.assertFalse(
            violations,
            "These OWL templates redeclare t-name == t-inherit in extension mode, which makes "
            "the override SHADOW (replace) the parent template in the JS template registry "
            "instead of extending it - the xpath edits silently become a no-op with no "
            "load-time error:\n%s\n\n"
            "Fix by DELETING the redundant t-name attribute - in extension mode the parent "
            "template name is already carried by t-inherit; t-name is never needed there."
            % _format_violations(REPO_ROOT, violations),
        )

    def test_scanner_actually_finds_extension_mode_templates(self):
        """Sanity gate: the guard above must not be vacuously green from an empty scan.

        A glob or attribute-name bug that silently matches zero files (or zero elements) would
        make the guard above pass for the wrong reason. This pins that the scan is genuinely
        discriminating: t-inherit-mode="extension" OWL templates exist in this worktree today.
        """
        paths = _static_src_xml_files(REPO_ROOT)
        self.assertTrue(paths, "no static/src/**/*.xml files found under %s" % REPO_ROOT)
        _violations, total = _self_shadowing_extensions(paths)
        self.assertGreater(
            total, 0,
            "scanner found zero t-inherit-mode=\"extension\" elements repo-wide - this means "
            "the scan itself is broken (wrong glob pattern or wrong attribute name), not that "
            "the repo genuinely has none: viin_brand_web alone ships several",
        )

    def test_synthetic_self_shadow_is_detected_and_clean_extension_is_not(self):
        """Pins the detector's discriminating logic against inline fixtures, independent of
        whatever this repo currently ships - proves the check can both fire and stay silent.
        """
        shadow_fixture = (
            '<templates xml:space="preserve">'
            '<t t-name="web.Foo" t-inherit="web.Foo" t-inherit-mode="extension" owl="1">'
            '<xpath expr="//div" position="replace"><div/></xpath>'
            "</t></templates>"
        )
        clean_fixture = (
            '<templates xml:space="preserve">'
            '<t t-inherit="web.Bar" t-inherit-mode="extension" owl="1">'
            '<xpath expr="//div" position="replace"><div/></xpath>'
            "</t>"
            '<t t-name="my_module.Distinct" t-inherit="web.Baz" t-inherit-mode="extension" owl="1">'
            '<xpath expr="//div" position="replace"><div/></xpath>'
            "</t></templates>"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            shadow_path = os.path.join(tmp_dir, "shadow.xml")
            clean_path = os.path.join(tmp_dir, "clean.xml")
            with open(shadow_path, "w", encoding="utf-8") as handle:
                handle.write(shadow_fixture)
            with open(clean_path, "w", encoding="utf-8") as handle:
                handle.write(clean_fixture)

            shadow_violations, shadow_total = _self_shadowing_extensions([shadow_path])
            self.assertEqual(len(shadow_violations), 1, "must flag the synthetic self-shadow")
            self.assertEqual(shadow_violations[0][2], "web.Foo")
            self.assertEqual(shadow_total, 1)

            clean_violations, clean_total = _self_shadowing_extensions([clean_path])
            self.assertFalse(
                clean_violations,
                "must NOT flag a t-name-less extension, nor one with a genuinely distinct "
                "t-name from its t-inherit target",
            )
            self.assertEqual(clean_total, 2)
