# <template inherit_id> targets a genuine ir.ui.view guard (ODOO-AI-ETHOS #8) - protects:
#
#   "Every `<template id=... inherit_id="X">` this repo ships must resolve X to a genuine
#    ir.ui.view record."
#
# WHY THIS MATTERS
# -----------------
# `odoo/tools/convert.py::_tag_template` hardcodes `model='ir.ui.view'` for any `<template>` tag
# in a non-`theme_*` module, REGARDLESS of what `inherit_id` actually names. `ref=` resolution
# then discards X's real model and writes X's raw numeric `res_id` straight into
# `ir.ui.view.inherit_id` - a real database foreign key (`ondelete='restrict'`). `ir_ui_view`
# carries thousands of rows across every installed module, so if X is NOT itself an `ir.ui.view`,
# this FK write can succeed silently against an unrelated row: the whole inheriting view becomes
# a permanent no-op with ZERO load-time error. `ir.ui.view._validate_module_views` only runs on
# `-u` (module upgrade), never on a fresh `-i` install, so a fresh-install deploy would never
# surface the break either.
#
# CLASS OF BUG GUARDED
# ---------------------
# A code review of this branch flagged exactly this shape as CRITICAL against
# viin_brand_auth_signup/data/auth_signup_templates_email.xml (target
# `auth_signup.reset_password_email`) - independently re-verified against 19.0 core source and
# `.po` comments (`model_terms:ir.ui.view,arch_db:...`) to be a FALSE POSITIVE for that specific
# target: it genuinely is an `ir.ui.view`. The finding was a false alarm this time, but the
# underlying defect CLASS is real (convert.py really does behave this way) and had zero prior
# automated coverage before this file - hence a general, repo-wide guard, re-derived from source
# every run, so a genuine future instance of the same shape is caught automatically instead of
# depending on another one-off manual review.
#
# DELIBERATE SCOPE LIMITS
# ------------------------
# 1. Only `<template id=... inherit_id="...">` in DATA/VIEW xml (anything outside `static/`).
#    `static/src/**` OWL templates use `t-inherit`, a different mechanism entirely - already
#    guarded by test_owl_extension_self_shadow.py in this same directory.
# 2. THE TARGET LIST IS NEVER HARDCODED. `_template_inherit_targets` re-parses the whole repo on
#    every test run, exactly like test_scss_variable_closure.py's reachability model - a newly
#    added `<template inherit_id=...>` anywhere is covered automatically, with no need to touch
#    this file in lockstep.
# 3. PARSED WITH REGEX, NOT AN XML TREE PARSER - same reasoning as
#    test_owl_extension_self_shadow.py (see that file's scope-limit 4 for the full rationale):
#    `defusedxml` is not a dependency this codebase carries, and a tag-level regex over trusted,
#    repo-local source avoids the stdlib tree parsers' XXE/entity-expansion exposure entirely.
# 4. THIS GUARD NEEDS A LIVE REGISTRY (`self.env.ref`) and therefore cannot be pure disk-parsing
#    like the guard above it - it only runs meaningfully under a real Odoo instance. It is
#    authored to the standard convention here and is unexecuted by the author of this file (no
#    live instance was available at authoring time); it runs for real at the next live re-verify.
import glob
import os
import re

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
REPO_ROOT = os.path.dirname(MODULE_DIR)

_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_TEMPLATE_TAG_RE = re.compile(r"<template\b([^>]*)>")
_ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def _view_xml_files(repo_root):
    """Every *.xml file in this repo EXCLUDING static/** (OWL, a different mechanism - see
    test_owl_extension_self_shadow.py) and EXCLUDING this module's own tests/ (never ships
    <template> records).
    """
    pattern = os.path.join(repo_root, "*", "**", "*.xml")
    files = []
    for path in glob.glob(pattern, recursive=True):
        parts = os.path.relpath(path, repo_root).split(os.sep)
        if "static" in parts or "tests" in parts:
            continue
        files.append(path)
    return sorted(files)


def _template_inherit_targets(repo_root):
    """[(path, template_id, inherit_id)] for every <template inherit_id="..."> in data/view xml.

    Re-parsed from source every call - never a hardcoded list - so a newly added template is
    picked up automatically instead of needing this file updated in lockstep. XML comments are
    stripped first so a commented-out example is never mistaken for a live template.
    """
    targets = []
    for path in _view_xml_files(repo_root):
        with open(path, "r", encoding="utf-8") as xml_file:
            stripped = _XML_COMMENT_RE.sub("", xml_file.read())
        for match in _TEMPLATE_TAG_RE.finditer(stripped):
            attrs = dict(_ATTR_RE.findall(match.group(1)))
            inherit_id = attrs.get("inherit_id")
            if inherit_id:
                targets.append((path, attrs.get("id"), inherit_id))
    return targets


@tagged("post_install", "-at_install")
class TemplateInheritIdTargetsViewTest(TransactionCase):

    def test_template_inherit_id_resolves_to_a_genuine_ir_ui_view(self):
        """Every <template inherit_id="X"> in this repo's data/view XML must resolve X to a
        genuine ir.ui.view record - see module header for why a non-view target is a silent,
        load-time-invisible no-op via ir.ui.view.inherit_id's raw foreign-key write.
        """
        targets = _template_inherit_targets(REPO_ROOT)
        self.assertTrue(
            targets,
            "no <template inherit_id=...> found repo-wide under %s - this likely means the scan "
            "itself is broken (see test_scanner_actually_finds_template_inherit_targets below), "
            "not that this repo genuinely ships none" % REPO_ROOT,
        )
        offenders = []
        for path, template_id, inherit_id in targets:
            try:
                target = self.env.ref(inherit_id)
            except ValueError:
                offenders.append(
                    "%s (template id=%r): inherit_id %r does not resolve to ANY record"
                    % (os.path.relpath(path, REPO_ROOT), template_id, inherit_id)
                )
                continue
            if target._name != "ir.ui.view":
                offenders.append(
                    "%s (template id=%r): inherit_id %r resolves to a %r record, not "
                    "ir.ui.view - convert.py will still write it into ir_ui_view.inherit_id, "
                    "silently corrupting an unrelated row and making this template a no-op"
                    % (os.path.relpath(path, REPO_ROOT), template_id, inherit_id, target._name)
                )
        self.assertFalse(offenders, "\n".join(offenders))

    def test_scanner_actually_finds_template_inherit_targets(self):
        """Sanity gate mirroring test_owl_extension_self_shadow.py's: pins that the scan is
        genuinely discriminating (non-empty), so the guard above cannot pass vacuously.
        """
        targets = _template_inherit_targets(REPO_ROOT)
        self.assertGreater(
            len(targets), 0,
            "scanner found zero <template inherit_id=...> repo-wide, which means the scan "
            "itself is broken - this repo ships many (e.g. "
            "viin_brand_auth_signup/data/auth_signup_templates_email.xml)",
        )

    def test_scanner_would_flag_a_non_view_target(self):
        """Sanity self-check for the rejection branch: picks a record that genuinely is NOT an
        ir.ui.view (base.main_company, standard in every Odoo database) and confirms
        `target._name != 'ir.ui.view'` - the exact condition the guard above uses to flag an
        offender - evaluates True for it. This shows what the guard WOULD report if a real
        <template inherit_id="..."> ever targeted a non-view record like this one, without
        needing a live broken fixture to exist in this repo today.
        """
        target = self.env.ref("base.main_company")
        self.assertNotEqual(
            target._name, "ir.ui.view",
            "base.main_company resolved to %r, not ir.ui.view - if this ever changes, Odoo's "
            "own base data has been restructured and this sanity check needs a new landmark "
            "record" % target._name,
        )
