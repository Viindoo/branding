# The cluster owns ZERO deliberate corner-radius overrides; every surface in it renders Odoo CE's
# native radius.
#
# THE BEHAVIOUR UNDER GUARD (owner revision 2026-08-03, "viec override bo tron dang duoc dien ra o
# nhieu cho, hay ra soat ky de bo het" - the radius overriding is happening in many places, audit
# thoroughly and remove them all). The theme used to raise the whole Bootstrap radius map
# ($border-radius 0.5rem / -sm 0.375rem / -lg 0.75rem, the "D13" scale) and then re-inject that
# inflated value into a dozen individual components. A later ruling, owner decision D5, kept ONE
# deliberate base-rung exception - a restored pre-19 brand-identity token,
# `$o-border-radius: 0 !default;` in viin_brand_web/static/src/scss/brand_variables.scss - while
# -sm/-lg and everything else stayed on core's own scale. Commit 52f233e ("remove border-radius
# override and link override") has since deleted that token outright, so D5 no longer exists as a
# live declaration anywhere in the cluster. The rule this file protects is once again the plain
# original one, with no exception left to carve out of it: NO source file in the cluster declares a
# corner radius at all, except the pinned shape-critical circles below.
#
# WHY THE SOURCE SCAN, NOT A COMPILED-CSS CHECK. A rule that writes `border-radius` DIRECTLY on a
# component (`.o_kanban_record`, `.o_loading_indicator`, the retired `999px` pills, the home menu
# tiles) never touches a Bootstrap token and would be invisible to a check of the compiled bundle -
# which is exactly how the previous pass' audit list grew to a dozen files before the owner asked
# for a sweep. Reading the authored SOURCE instead catches that class of regression directly, and
# it turns RED the moment anyone re-adds a radius anywhere in the cluster outside the allow-list.
#
# SASS VARIABLES ARE SCANNED TOO, not just CSS declarations: the original D13 regression entered as
# `$border-radius: 0.5rem`, which emits no `border-radius:` text at all in the file that causes it.
# It is also how the now-removed D5 token was caught and pinned here for as long as it existed.
#
# SHAPE-CRITICAL EXCEPTIONS, and why an allow-list rather than a looser regex. A declaration
# survives the sweep only when the radius IS the element's identity rather than a rounding taste -
# `border-radius: 50%` on the skeleton avatar placeholder (`.o_viin_skeleton_circle`), or on the
# statusbar step-number badge. Removing either does not make the element less rounded, it makes it a
# different element. Each is pinned as an exact (path, declaration) pair rather than as a "50% is
# fine" rule, so a THIRD circle added tomorrow still fails and gets an explicit decision.
# (The D6 stepper's `.o_viin_step_marker` was an earlier entry. The owner reverted that whole
# stepper on 2026-08-03 - core's arrow statusbar is back - so viin_backend_theme's
# statusbar_field.scss is gone and its exception with it; its absence from this list stays
# load-bearing, and re-adding that THEME file would fail the sweep. The numbering affordance the
# owner did ask back for was re-implemented on the same day as an additive marker in
# viin_brand_web - no pill, no clip-path, no container chrome - and is listed on its own path.)
import os
import re

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged

# The cluster this invariant covers. Modules absent from the addons path are skipped, not failed, so
# the guard survives a repackaging; a module that IS present is always scanned, installed or not.
CLUSTER_MODULES = (
    "viin_backend_theme",
    "viin_brand_mail",
    "viin_brand_web",
    "viin_brand_html_editor",
    "viin_brand",
)
SCANNED_SUFFIXES = (".scss", ".css", ".xml", ".js")
# tests own their fixtures; static/lib is vendored third-party code the cluster does not author.
SKIPPED_DIR_PARTS = (os.sep + "tests" + os.sep, os.sep + "lib" + os.sep, os.sep + "node_modules" + os.sep)

# SHAPE-CRITICAL allow-list: (module-relative path, exact declaration). See the header for why each
# one is a shape and not a rounding tweak. Anything else that declares a radius fails.
ALLOWED_RADIUS_DECLARATIONS = {
    # `.o_viin_skeleton_circle` is a round avatar placeholder; 50% IS the modifier's whole meaning.
    ("viin_backend_theme", "static/src/skeleton/skeleton.scss"): {"border-radius:50%"},
    # The PWA offline fallback page is standalone HTML with NO Odoo/Bootstrap stylesheet loaded, so
    # this inline rule is not overriding anything - it is the only styling source on that page, and
    # .25rem is already exactly core's $o-border-radius. Deleting it would square the button, i.e.
    # move FURTHER from Odoo CE rather than closer, which is the opposite of this file's rule.
    ("viin_brand_web", "views/webclient_template.xml"): {"border-radius:.25rem"},
    # The statusbar STEP-NUMBER marker (owner request 2026-08-03: the step numbers came back on
    # core's arrow steps). `50%` on a `::after` box whose entire content is a single digit: the
    # circle IS the marker - squared, it stops reading as a step badge and becomes a stray number
    # against the label. Two things make it a shape and not a rounding tweak, and both are why it
    # is admitted here rather than deleted:
    #   * it is on a PSEUDO-ELEMENT, so it rounds nothing the user can otherwise see - no button,
    #     card, input or panel corner moves, which is the whole complaint this file protects;
    #   * it cannot leak. `border-radius: 50%` is meaningless on any box that is not the marker,
    #     and the selector reaches exactly one: `.o_arrow_button.o_viin_numbered_step::after`.
    # This is the successor to the D6 stepper's `.o_viin_step_marker` entry the header describes.
    # That one came with a whole pill restyle (clip-path: none, container padding) and was reverted
    # WITH it; this one is the numbering affordance ALONE, which is the part the owner asked back.
    ("viin_brand_web", "static/src/views/fields/statusbar/statusbar_steps.scss"):
        {"border-radius:50%"},
}

# A radius declaration in authored source: a CSS/custom property `(-*)border-radius:` or a Sass
# variable assignment whose name mentions radius (`$border-radius`, `$btn-border-radius-sm`,
# `$o-border-radius`, ...). Both forms are needed: the D13 regression came in as the Sass form.
# `#{...}` interpolation is matched WHOLE rather than stopping at its brace, so the failure message
# quotes `--modal-border-radius: #{$border-radius}` instead of a useless truncated `... : #`.
_VALUE = r"(?:[^;{}]|#\{[^}]*\})*"
_SOURCE_RADIUS_RE = re.compile(
    r"(?:[\w-]*border-[\w-]*radius\s*:" + _VALUE + r"|\$[\w-]*radius[\w-]*\s*:" + _VALUE + r")"
)
_SCSS_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _strip_comments(text, path):
    text = _BLOCK_COMMENT_RE.sub("", text)
    if path.endswith(".xml"):
        return _XML_COMMENT_RE.sub("", text)
    return _SCSS_LINE_COMMENT_RE.sub("", text)


@tagged("post_install", "-at_install")
class TestThemeRadiusIsCore(TransactionCase):
    """Every surface renders Odoo CE's native radius; the cluster declares no override of its own.

    Owner decision D5's base-rung exception (`$o-border-radius: 0 !default;` in
    viin_brand_web/static/src/scss/brand_variables.scss) was removed in commit 52f233e, so no
    declaration anywhere in the cluster is exempted any more except the shape-critical circles
    pinned in ALLOWED_RADIUS_DECLARATIONS. See the module header for the full lineage.
    """

    def test_the_cluster_declares_no_radius_of_its_own(self):
        """No cluster source file declares a corner radius, except the shape-critical circles
        pinned in ALLOWED_RADIUS_DECLARATIONS.

        Owner decision D5's base-rung square-corners token was removed in commit 52f233e, so this
        invariant no longer carves out any exception beyond the shape-critical circles: any radius
        declaration found anywhere else in the cluster fails, full stop.

        THE ASSERTION A COMPILED-CSS CHECK CANNOT MAKE. A rule that writes `border-radius` DIRECTLY
        on a component (`.o_kanban_record`, `.o_loading_indicator`, the retired `999px` pills, the
        home menu tiles) never touches a Bootstrap token, so a check of the compiled bundle would
        stay green while the surface is visibly rounder than core. That is precisely how the
        override count grew to a dozen files before the owner asked for a sweep. This scan is the
        only thing that keeps the cluster at the shape-critical-only baseline.

        SASS VARIABLES ARE SCANNED TOO, not just CSS declarations: the original D13 regression
        entered as `$border-radius: 0.5rem`, which emits no `border-radius:` text at all in the
        file that causes it.

        RED BEFORE GREEN: re-adding any single removed line - e.g. `border-radius: $border-radius`
        to views/kanban/kanban_record.scss - names the file, the line number and the declaration.
        A radius declaration re-added to brand_variables.scss, or anywhere else in the cluster,
        goes RED the same way."""
        offenders = []
        scanned_modules = []
        for module in CLUSTER_MODULES:
            module_path = get_module_path(module, display_warning=False)
            if not module_path:
                continue
            scanned_modules.append(module)
            allowed = ALLOWED_RADIUS_DECLARATIONS
            for root, _dirs, files in os.walk(module_path):
                for filename in sorted(files):
                    if not filename.endswith(SCANNED_SUFFIXES):
                        continue
                    absolute = os.path.join(root, filename)
                    relative = os.path.relpath(absolute, module_path).replace(os.sep, "/")
                    if any(part in absolute + os.sep for part in SKIPPED_DIR_PARTS):
                        continue
                    with open(absolute, "r", encoding="utf-8") as handle:
                        source = handle.read()
                    stripped = _strip_comments(source, filename)
                    permitted = allowed.get((module, relative), set())
                    for match in _SOURCE_RADIUS_RE.finditer(stripped):
                        declaration = re.sub(r"\s+", "", match.group(0)).rstrip(";")
                        if declaration in permitted:
                            continue
                        line = stripped.count("\n", 0, match.start()) + 1
                        offenders.append(
                            "%s/%s (near line %d of the comment-stripped file): %s"
                            % (module, relative, line, match.group(0).strip())
                        )

        self.assertTrue(
            scanned_modules,
            "None of %s resolved on the addons path, so this guard scanned nothing and would pass "
            "vacuously. Re-ground CLUSTER_MODULES on the cluster's real module names."
            % (CLUSTER_MODULES,),
        )
        self.assertFalse(
            offenders,
            "The cluster is supposed to own ZERO corner-radius declarations, so every surface "
            "renders Odoo CE's native radius (owner revision 2026-08-03, 'bo het'; the D5 "
            "square-corners exception this rule once carved out of that sweep was itself removed "
            "in commit 52f233e), but %d declaration(s) were found beyond the allow-list:\n  %s\n\n"
            "Delete them - do NOT replace one override with another, and do not widen the "
            "allow-list unless the declaration is genuinely SHAPE-critical (a circle that would "
            "otherwise become a square) or is a new, deliberate, owner-approved override, in which "
            "case add it to ALLOWED_RADIUS_DECLARATIONS with the reasoning, the way the 50%% "
            "skeleton avatar is handled."
            % (len(offenders), "\n  ".join(offenders)),
        )
