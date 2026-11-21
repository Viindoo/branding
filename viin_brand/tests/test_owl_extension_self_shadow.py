# OWL extension self-shadow guard. The business rule:
#
#   "No OWL/QWeb template in `t-inherit-mode="extension"` may redeclare `t-name` equal to its
#    own `t-inherit` target."
#
# When `t-name` duplicates `t-inherit` on a `t-inherit-mode="extension"` element, the JS template
# registry treats the extension arch as a replacement of the parent template (same registry key,
# last one registered wins) instead of an extension of it. The xpath edits silently become a no-op
# with no load-time error: the template still loads and renders as the unmodified parent. Core
# never does this - its extension-mode templates either omit `t-name` or use a distinct name.
#
# Scope:
# 1. Every `*.xml` under any module's `static/src/**` in the whole repo, since the mechanism is
#    JS-registry-wide and a violation in any module can shadow a template another module touches.
# 2. The repo is re-scanned from disk on every run, with no allow-list of known offenders.
# 3. `t-inherit-mode="extension"` only. `t-inherit-mode="primary"` legitimately needs its own
#    `t-name`; in `extension` mode `t-name` is redundant because `t-inherit` carries the target.
# 4. Parsed with a tag-level regex, not an XML tree parser: the stdlib tree parsers carry known
#    XXE/entity-expansion exposure that a regex over trusted, repo-local source never needs to
#    accept, and `defusedxml` is not a dependency of this codebase. XML comments are stripped
#    first so a commented-out example is not mistaken for a live tag.
#
# Everything is read from disk. A TransactionCase whose assertions never touch self.env is the
# pattern of this module for static file-parsing guards (see test_scss_variable_closure.py).
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

    OWL extension templates are single-line (`<t t-name=... t-inherit=...
    t-inherit-mode="extension" ...>`); a template laid out differently yields `None` rather than
    a wrong line.
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
    total_extension_elements: count of all t-inherit-mode="extension" elements scanned, which
    lets a caller prove the scan is not vacuously passing.
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
        """The scan must find extension-mode templates, so the guard above is not vacuously green.

        A glob or attribute-name bug that matches zero files or elements would make that guard
        pass for the wrong reason.
        """
        paths = _static_src_xml_files(REPO_ROOT)
        self.assertTrue(paths, "no static/src/**/*.xml files found under %s" % REPO_ROOT)
        _violations, total = _self_shadowing_extensions(paths)
        self.assertGreater(
            total, 0,
            "scanner found zero t-inherit-mode=\"extension\" elements repo-wide - this means "
            "the scan itself is broken (wrong glob pattern or wrong attribute name), not that "
            "the repo genuinely has none: viin_brand alone ships several",
        )

    def test_synthetic_self_shadow_is_detected_and_clean_extension_is_not(self):
        """The detector fires on a synthetic self-shadow and stays silent on a clean extension.
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
