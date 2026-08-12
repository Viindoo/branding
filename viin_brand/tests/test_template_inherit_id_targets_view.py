# <template inherit_id> targets a genuine ir.ui.view guard (ODOO-AI-ETHOS #8) - protects:
#
#   "Every `<template id=... inherit_id="X">` shipped by an INSTALLED module of this repo must
#    resolve X to a genuine ir.ui.view record."
#
# WHY THIS MATTERS
# -----------------
# `odoo/tools/convert.py::_tag_template` hardcodes `model='ir.ui.view'` for any `<template>` tag
# in a non-`theme_*` module, REGARDLESS of what `inherit_id` actually names (`convert.py:483-486`).
# It then emits `Field(name='inherit_id', ref=X)` (`convert.py:508`), and `id_get`
# (`convert.py:585-589`) discards X's real MODEL and keeps only X's raw numeric `res_id`. That
# bare number is written straight into `ir.ui.view.inherit_id` - a real database foreign key
# (`ir_ui_view.py:169`, `ondelete='restrict'`). `ir_ui_view` carries thousands of rows across every
# installed module, so if X is NOT itself an `ir.ui.view`, the FK write can land on a completely
# unrelated view row and the inheriting template becomes a permanent no-op pointed at the wrong
# parent.
#
# HOW VISIBLE IS THE FAILURE: CONDITIONALLY SILENT, DATA-DEPENDENT
# -----------------------------------------------------------------
# NOT unconditionally silent. An earlier revision of this header claimed the break lands with
# "ZERO load-time error" and that `_validate_module_views` only runs on `-u`, so a fresh `-i`
# install would never surface it. THAT CLAIM IS WRONG and is corrected here: `_check_xml` runs on
# `create` (`ir_ui_view.py:641`) and on `write` (`ir_ui_view.py:664`), not only on upgrade. Inside
# it, `_get_combined_arch()` (`ir_ui_view.py:442`) is called BEFORE the
# `if view.type == 'qweb': continue` guard (`ir_ui_view.py:476-477`), so a spec that cannot be
# located in the wrong parent raises out of `template_inheritance.py:144-146` and is re-raised as a
# `ValidationError` (`ir_ui_view.py:478-486`). LOUDLY, on a plain `-i`.
#
# The accurate statement is that the failure is CONDITIONALLY SILENT and DATA-DEPENDENT. To go
# silent it needs BOTH of:
#   (a) the non-view record's `res_id` to coincide with a real `ir_ui_view` id - otherwise the FK
#       constraint itself blows up first; AND
#   (b) the spec to still locate inside that WRONG parent - typically an
#       `<xpath expr="." position="inside"/>`, or a selector generic enough to match anywhere.
# This repo currently ships ZERO `expr="."` outside `static/`, so the easiest-to-silence shape is
# not present today - which is a fact about today's source, not a property of the defect.
#
# That data-dependence is precisely WHY a static, source-derived guard earns its place: whether the
# bug explodes or goes quiet depends on which record ids happen to exist in the particular database
# it is installed into, so NO runtime test reproduces it reliably. Rather than wait for a database
# whose id layout happens to hide it, this guard checks the source on every run.
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
# THE SCOPE KEY IS THE SHIPPING MODULE, NOT THE TARGET MODULE
# ------------------------------------------------------------
# Resolving every scanned `inherit_id` through `self.env.ref` on any database, unconditionally,
# is STRUCTURALLY UNABLE TO PASS: it conflates "this target is genuinely broken" with "the module
# that owns the target simply is not installed on THIS database". Measured on 19.0 source, all 52
# targets in this repo resolve to genuine `ir.ui.view` records, yet the unconditional form reported
# 46 offenders on a 4-module instance and 29 on a 97-module instance - every single one a false
# alarm about an absent module, never a real defect.
#
# The correct key is whether the module that SHIPS the `<template>` is installed:
#   * SHIPPING MODULE INSTALLED   -> `convert.py` has already processed that `<template>`, so every
#     `inherit_id` it names MUST have resolved or the install would have aborted. Checking it is
#     meaningful, and it MUST be green.
#   * SHIPPING MODULE ABSENT      -> the `<template>` was never converted, no FK row was ever
#     written, there is literally nothing to protect. Skipping loses ZERO real coverage.
# This does NOT create a cross-module blind spot: if module A IS installed and one of its templates
# points at `moduleB.X` while B is absent, this key still CHECKS it and still REPORTS it -
# correctly, because that IS a genuine install-time failure of A.
#
# DELIBERATE SCOPE LIMITS
# ------------------------
# 1. Only `<template id=... inherit_id="...">` in DATA/VIEW xml (anything outside `static/`).
#    `static/src/**` OWL templates use `t-inherit`, a different mechanism entirely - already
#    guarded by viin_brand_web/tests/test_owl_extension_self_shadow.py.
# 2. THE TARGET LIST IS NEVER HARDCODED. `_template_inherit_targets` re-parses the whole repo on
#    every test run, exactly like test_scss_variable_closure.py's reachability model - a newly
#    added `<template inherit_id=...>` anywhere is covered automatically, with no need to touch
#    this file in lockstep. The INSTALLED-module set is likewise resolved live from
#    `ir.module.module`, never from a hardcoded module list.
# 3. PARSED WITH REGEX, NOT AN XML TREE PARSER - same reasoning as
#    test_owl_extension_self_shadow.py (see that file's scope-limit 4 for the full rationale):
#    `defusedxml` is not a dependency this codebase carries, and a tag-level regex over trusted,
#    repo-local source avoids the stdlib tree parsers' XXE/entity-expansion exposure entirely.
# 4. THIS GUARD NEEDS A LIVE REGISTRY (`self.env.ref`, `ir.module.module`) and therefore cannot be
#    pure disk-parsing - it only runs meaningfully under a real Odoo instance. It lives in
#    `viin_brand` (not in the module it happens to have been drafted in) because it imports NO Odoo
#    module symbol at all and touches only `self.env`: it needs no dependency on anything it scans,
#    only to be installed. `viin_brand` is `depends: ['base', 'web']` with `auto_install: True`, so
#    it is present on every database that has `web` - the broadest reach available to a repo-wide
#    guard, at the cost of zero new dependency edges anywhere.
# 5. THE SKIP IS REPORTED, NOT HIDDEN. A guard that quietly narrows its own scope rots into a
#    no-op, which is the very bug class this file exists to prevent. So the checked/skipped counts
#    and the skipped module names are logged on every run and repeated in the failure message, and
#    `test_scan_covers_every_installed_repo_module_that_ships_such_a_template` pins the scanned set
#    by EXACT SET EQUALITY against a SECOND, independently implemented oracle (`os.walk` +
#    `str.split`, sharing no code path with the glob+regex scanner). A future edit that silently
#    makes the scanner match fewer files fails there. That oracle is deliberately DISK-based rather
#    than registry-based: a live-registry oracle ("installed repo modules owning a qweb ir.ui.view
#    with inherit_id") demonstrably diverges, because viin_brand_website_forum ships that same shape
#    as a plain `<record model="ir.ui.view">` rather than a `<template>` - out of scope here.
import glob
import logging
import os
import re

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
REPO_ROOT = os.path.dirname(MODULE_DIR)

_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_TEMPLATE_TAG_RE = re.compile(r"<template\b([^>]*)>")
_ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')

# Directory names never scanned: OWL sources (a different inheritance mechanism, scope-limit 1)
# and test packages (never ship <template> records).
_SKIPPED_DIRS = ("static", "tests")


def _view_xml_files(repo_root):
    """Every *.xml file in this repo EXCLUDING static/** (OWL, a different mechanism - see
    viin_brand_web/tests/test_owl_extension_self_shadow.py) and EXCLUDING tests/** (never ships
    <template> records).
    """
    pattern = os.path.join(repo_root, "*", "**", "*.xml")
    files = []
    for path in glob.glob(pattern, recursive=True):
        parts = os.path.relpath(path, repo_root).split(os.sep)
        if any(skipped in parts for skipped in _SKIPPED_DIRS):
            continue
        files.append(path)
    return sorted(files)


def _shipping_module(path, repo_root):
    """The repo module that SHIPS `path` - its first path segment under the repo root.

    This is the guard's SCOPE KEY (see header): the module whose install made `convert.py`
    actually convert the `<template>`, which is what decides whether there is anything to protect.
    """
    return os.path.relpath(path, repo_root).split(os.sep)[0]


def _template_inherit_targets(repo_root):
    """[(path, shipping_module, template_id, inherit_id)] for every <template inherit_id="...">
    in data/view xml.

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
                targets.append(
                    (path, _shipping_module(path, repo_root), attrs.get("id"), inherit_id)
                )
    return targets


def _modules_shipping_template_inherit(repo_root):
    """INDEPENDENT oracle: the set of repo modules shipping >=1 `<template ... inherit_id=...>`.

    Deliberately a SECOND, dumber implementation of the same question, sharing NO code path with
    `_view_xml_files` / `_template_inherit_targets`: `os.walk` instead of `glob`, and plain
    `str.split` instead of the compiled regexes. That independence is the whole point - if both
    sides were the same code, the equality gate that consumes this would be a tautology and could
    not catch a scanner that silently stopped matching files.
    """
    modules = set()
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [
            name for name in dirnames
            if name not in _SKIPPED_DIRS and not name.startswith(".")
        ]
        relative = os.path.relpath(dirpath, repo_root)
        if relative == os.curdir:
            continue
        module = relative.split(os.sep)[0]
        if module in modules:
            continue
        for filename in filenames:
            if not filename.endswith(".xml"):
                continue
            with open(os.path.join(dirpath, filename), "r", encoding="utf-8") as xml_file:
                raw = xml_file.read()
            # Drop commented-out regions, same semantics as _XML_COMMENT_RE but by a different
            # mechanism: keep only what follows each comment close.
            live = "".join(chunk.split("-->")[-1] for chunk in raw.split("<!--"))
            # An opening `<template ...>` tag carrying inherit_id: everything up to the first '>'.
            opening_tags = [chunk.split(">", 1)[0] for chunk in live.split("<template")[1:]]
            if any("inherit_id=" in tag for tag in opening_tags):
                modules.add(module)
                break
    return modules


def _installed(env, modules):
    """The subset of `modules` in state 'installed' on THIS database - read live from
    ir.module.module, never a hardcoded list (scope-limit 2).
    """
    if not modules:
        return set()
    installed = env["ir.module.module"].search([
        ("name", "in", sorted(modules)),
        ("state", "=", "installed"),
    ])
    return set(installed.mapped("name"))


@tagged("post_install", "-at_install")
class TemplateInheritIdTargetsViewTest(TransactionCase):

    def test_template_inherit_id_resolves_to_a_genuine_ir_ui_view(self):
        """Every <template inherit_id="X"> shipped by an INSTALLED repo module must resolve X to a
        genuine ir.ui.view record - see module header for why a non-view target is a
        conditionally-silent, data-dependent no-op via ir.ui.view.inherit_id's raw foreign-key
        write, and for why the SHIPPING module (not the target's module) is the scope key.
        """
        targets = _template_inherit_targets(REPO_ROOT)
        self.assertTrue(
            targets,
            "no <template inherit_id=...> found repo-wide under %s - this likely means the scan "
            "itself is broken (see test_scanner_actually_finds_template_inherit_targets below), "
            "not that this repo genuinely ships none" % REPO_ROOT,
        )
        shipping_modules = {module for _path, module, _tpl, _inherit in targets}
        installed = _installed(self.env, shipping_modules)
        skipped_modules = shipping_modules - installed

        checked = 0
        offenders = []
        for path, module, template_id, inherit_id in targets:
            if module not in installed:
                # Not installed => convert.py never processed this <template>, no inherit_id FK was
                # ever written, nothing to protect. Reported below, never hidden.
                continue
            checked += 1
            try:
                target = self.env.ref(inherit_id)
            except ValueError:
                offenders.append(
                    "%s (template id=%r): inherit_id %r does not resolve to ANY record, even "
                    "though its shipping module %r IS installed - convert.py must already have "
                    "resolved it at install time, so this is a genuine broken reference"
                    % (os.path.relpath(path, REPO_ROOT), template_id, inherit_id, module)
                )
                continue
            if target._name != "ir.ui.view":
                offenders.append(
                    "%s (template id=%r): inherit_id %r resolves to a %r record, not "
                    "ir.ui.view - convert.py will still write it into ir_ui_view.inherit_id, "
                    "silently corrupting an unrelated row and making this template a no-op"
                    % (os.path.relpath(path, REPO_ROOT), template_id, inherit_id, target._name)
                )

        scope = (
            "scope: %d/%d <template inherit_id> checked, %d skipped as not-installed "
            "(installed shipping modules: %s | skipped shipping modules: %s)"
            % (
                checked,
                len(targets),
                len(targets) - checked,
                ", ".join(sorted(installed)) or "<none>",
                ", ".join(sorted(skipped_modules)) or "<none>",
            )
        )
        # Logged on EVERY run, green included: a skip nobody can see is how a guard rots into a
        # no-op (header scope-limit 5).
        _logger.info("template inherit_id guard - %s", scope)
        self.assertFalse(offenders, "%s\n%s" % (scope, "\n".join(offenders)))

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

    def test_scan_covers_every_installed_repo_module_that_ships_such_a_template(self):
        """Anti-scope-shrink gate: the modules the guard actually CHECKS must be EXACTLY the
        installed repo modules that ship a `<template inherit_id=...>` - an exact set equality,
        never a "looks big enough" threshold.

        The right-hand side comes from `_modules_shipping_template_inherit`, a second and
        deliberately independent implementation (os.walk + str.split, no shared code path with the
        glob+regex scanner). If a later edit narrows the scanner so it silently matches fewer
        files - the failure mode that turns a guard into a green no-op - the two sides diverge and
        this fails.
        """
        oracle = _modules_shipping_template_inherit(REPO_ROOT)
        self.assertTrue(
            oracle,
            "the independent oracle found zero repo modules shipping a <template inherit_id=...>, "
            "so the ORACLE itself is broken and cannot pin anything - fix "
            "_modules_shipping_template_inherit before trusting any result from this file",
        )
        targets = _template_inherit_targets(REPO_ROOT)
        shipping_modules = {module for _path, module, _tpl, _inherit in targets}
        installed = _installed(self.env, shipping_modules | oracle)

        scanned = shipping_modules & installed
        expected = oracle & installed
        self.assertEqual(
            scanned, expected,
            "the set of modules this guard actually checks has drifted from the set of installed "
            "repo modules that ship a <template inherit_id=...>.\n"
            "  checked but not expected: %s\n"
            "  expected but NOT checked: %s\n"
            "The second list is the dangerous one: those modules ship templates that this guard "
            "silently stopped covering."
            % (
                ", ".join(sorted(scanned - expected)) or "<none>",
                ", ".join(sorted(expected - scanned)) or "<none>",
            ),
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
