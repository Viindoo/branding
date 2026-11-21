# <template inherit_id> targets a genuine ir.ui.view. The rule:
#
#   "Every `<template id=... inherit_id="X">` shipped by an INSTALLED module of this repo must
#    resolve X to a genuine ir.ui.view record."
#
# `odoo/tools/convert.py::_tag_template` hardcodes `model='ir.ui.view'` for any `<template>` tag in
# a non-`theme_*` module, regardless of what `inherit_id` names. It emits
# `Field(name='inherit_id', ref=X)`, and `id_get` discards X's real model and keeps only its raw
# numeric `res_id`. That number is written into `ir.ui.view.inherit_id`, a real database foreign
# key. If X is not itself an `ir.ui.view`, the write can land on an unrelated view row and the
# inheriting template becomes a permanent no-op pointed at the wrong parent.
#
# The failure is conditionally silent and data-dependent. `_check_xml` runs on create and write,
# and `_get_combined_arch()` runs before the `view.type == 'qweb'` guard, so a spec that cannot be
# located in the wrong parent raises a ValidationError on a plain `-i`. It goes silent only when
# BOTH hold:
#   (a) the non-view record's `res_id` coincides with a real `ir_ui_view` id (otherwise the FK
#       constraint fails first); and
#   (b) the spec still locates inside that wrong parent, e.g. an `<xpath expr="." position="inside"/>`
#       or a selector generic enough to match anywhere.
# Which record ids exist depends on the database, so no runtime test reproduces it reliably; this
# guard checks the source on every run.
#
# The scope key is the shipping module, not the target module. Resolving every scanned `inherit_id`
# through `self.env.ref` on any database conflates "this target is broken" with "the module that
# owns the target is not installed on THIS database". The key is whether the module that ships the
# `<template>` is installed:
#   * shipping module installed -> `convert.py` processed that `<template>`, so every `inherit_id`
#     it names must have resolved or the install would have aborted; the check is meaningful.
#   * shipping module absent    -> the `<template>` was never converted and no FK row was written;
#     skipping loses no coverage.
# If module A is installed and one of its templates points at `moduleB.X` while B is absent, the
# check still reports it, correctly: that is an install-time failure of A.
#
# Scope:
# 1. Only `<template id=... inherit_id="...">` in data/view xml (anything outside `static/`).
#    `static/src/**` OWL templates use `t-inherit`, a different mechanism guarded by
#    tests/test_owl_extension_self_shadow.py.
# 2. The target list is re-parsed from the repo on every run, and the installed-module set is
#    resolved live from `ir.module.module`; nothing is hardcoded.
# 3. Parsed with a tag-level regex, not an XML tree parser, for the reasons given in
#    tests/test_owl_extension_self_shadow.py.
# 4. The guard needs a live registry (`self.env.ref`, `ir.module.module`). It lives in `viin_brand`
#    because it imports no Odoo module symbol and touches only `self.env`; `viin_brand` is
#    `auto_install` on `web`, so it is present on every database that has `web`.
# 5. The skip is reported, not hidden: the checked/skipped counts and skipped module names are
#    logged on every run and repeated in the failure message, and
#    `test_scan_covers_every_installed_repo_module_that_ships_such_a_template` pins the scanned set
#    by exact set equality against a second, independently implemented oracle (`os.walk` +
#    `str.split`, sharing no code path with the glob+regex scanner). The oracle is disk-based
#    rather than registry-based because a registry oracle diverges: viin_brand_website_forum ships
#    the same shape as a plain `<record model="ir.ui.view">`, which is out of scope here.
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

# Directory names never scanned: OWL sources (a different inheritance mechanism) and test packages
# (never ship <template> records).
_SKIPPED_DIRS = ("static", "tests")


def _view_xml_files(repo_root):
    """Every *.xml file in this repo EXCLUDING static/** (OWL, a different mechanism - see
    viin_brand/tests/test_owl_extension_self_shadow.py) and EXCLUDING tests/** (never ships
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
    """The repo module that ships `path` - its first path segment under the repo root.

    This is the guard's scope key (see header): the module whose install made `convert.py`
    convert the `<template>`.
    """
    return os.path.relpath(path, repo_root).split(os.sep)[0]


def _template_inherit_targets(repo_root):
    """[(path, shipping_module, template_id, inherit_id)] for every <template inherit_id="...">
    in data/view xml.

    Re-parsed from source on every call. XML comments are stripped first so a commented-out
    example is not mistaken for a live template.
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
    """Independent oracle: the set of repo modules shipping at least one
    `<template ... inherit_id=...>`.

    A second implementation of the same question that shares no code path with `_view_xml_files` /
    `_template_inherit_targets` (`os.walk` instead of `glob`, `str.split` instead of regexes), so
    the equality gate that consumes it is not a tautology.
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
            # Drop commented-out regions: keep only what follows each comment close.
            live = "".join(chunk.split("-->")[-1] for chunk in raw.split("<!--"))
            # An opening `<template ...>` tag carrying inherit_id: everything up to the first '>'.
            opening_tags = [chunk.split(">", 1)[0] for chunk in live.split("<template")[1:]]
            if any("inherit_id=" in tag for tag in opening_tags):
                modules.add(module)
                break
    return modules


def _installed(env, modules):
    """The subset of `modules` in state 'installed' on this database."""
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
        """Every <template inherit_id="X"> shipped by an installed repo module must resolve X to a
        genuine ir.ui.view record; see the module header for the failure mode and the scope key.
        """
        targets = _template_inherit_targets(REPO_ROOT)
        self.assertTrue(
            targets,
            "no <template inherit_id=...> found repo-wide under %s - the scan itself is likely "
            "broken (see test_scanner_actually_finds_template_inherit_targets)" % REPO_ROOT,
        )
        shipping_modules = {module for _path, module, _tpl, _inherit in targets}
        installed = _installed(self.env, shipping_modules)
        skipped_modules = shipping_modules - installed

        checked = 0
        offenders = []
        for path, module, template_id, inherit_id in targets:
            if module not in installed:
                # Not installed: convert.py never processed this <template>. Reported below.
                continue
            checked += 1
            try:
                target = self.env.ref(inherit_id)
            except ValueError:
                offenders.append(
                    "%s (template id=%r): inherit_id %r does not resolve to ANY record, even "
                    "though its shipping module %r is installed - convert.py resolves it at "
                    "install time, so this is a broken reference"
                    % (os.path.relpath(path, REPO_ROOT), template_id, inherit_id, module)
                )
                continue
            if target._name != "ir.ui.view":
                offenders.append(
                    "%s (template id=%r): inherit_id %r resolves to a %r record, not "
                    "ir.ui.view - convert.py writes it into ir_ui_view.inherit_id, which "
                    "corrupts an unrelated row and makes this template a no-op"
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
        # Logged on every run, green included, so a narrowed scope is visible.
        _logger.info("template inherit_id guard - %s", scope)
        self.assertFalse(offenders, "%s\n%s" % (scope, "\n".join(offenders)))

    def test_scanner_actually_finds_template_inherit_targets(self):
        """The scan finds targets, so the guard above cannot pass vacuously."""
        targets = _template_inherit_targets(REPO_ROOT)
        self.assertGreater(
            len(targets), 0,
            "scanner found zero <template inherit_id=...> repo-wide, which means the scan "
            "itself is broken - this repo ships many",
        )

    def test_scan_covers_every_installed_repo_module_that_ships_such_a_template(self):
        """The modules the guard checks are exactly the installed repo modules that ship a
        `<template inherit_id=...>`.

        The expected side comes from `_modules_shipping_template_inherit`, which shares no code
        path with the glob+regex scanner, so a scanner that silently matches fewer files makes the
        two sides diverge.
        """
        oracle = _modules_shipping_template_inherit(REPO_ROOT)
        self.assertTrue(
            oracle,
            "the independent oracle found zero repo modules shipping a <template inherit_id=...>, "
            "so the oracle itself is broken - fix _modules_shipping_template_inherit",
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
        """The condition the guard uses to flag an offender (`target._name != 'ir.ui.view'`) is
        true for a record that is not an ir.ui.view (base.main_company, present in every database).
        """
        target = self.env.ref("base.main_company")
        self.assertNotEqual(
            target._name, "ir.ui.view",
            "base.main_company is an %r - this check needs another non-view record" % target._name,
        )
