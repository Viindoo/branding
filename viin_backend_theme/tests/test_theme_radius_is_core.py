import os
import re

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged

# Modules absent from the addons path are skipped, so the guard survives a repackaging; a module
# that is present is always scanned, installed or not.
CLUSTER_MODULES = (
    "viin_backend_theme",
    "viin_brand_mail",
    "viin_brand_html_editor",
    "viin_brand",
)

# Shape-critical radii: (module, module-relative path) -> exact declarations. A radius survives only
# when it IS the element's identity, and each one is pinned as an exact pair rather than a "50% is
# fine" rule, so a further circle still fails and gets an explicit decision.
ALLOWED_RADIUS_DECLARATIONS = {
    # `.o_viin_skeleton_circle` is a round avatar placeholder; 50% is the modifier's whole meaning.
    ("viin_backend_theme", "static/src/skeleton/skeleton.scss"): {"border-radius:50%"},
    # The PWA offline page is standalone HTML with no Odoo stylesheet, so this inline rule overrides
    # nothing; .25rem is core's own $o-border-radius.
    ("viin_brand", "views/webclient_templates.xml"): {"border-radius:.25rem"},
    # The statusbar step-number badge: 50% on a `::after` holding one digit. It rounds no visible
    # button, card or input, and its selector reaches only `.o_arrow_button.o_viin_numbered_step::after`.
    ("viin_brand", "static/src/views/fields/statusbar/statusbar_steps.scss"):
        {"border-radius:50%"},
}

# A radius declaration in authored source: a CSS/custom property `(-*)border-radius:` or a Sass
# variable whose name mentions radius (`$border-radius`, `$o-border-radius`, ...). The Sass form
# emits no `border-radius:` text in the file that declares it. `#{...}` interpolation is matched
# whole so a failure quotes `--modal-border-radius: #{$border-radius}`, not a truncated `... : #`.
_SOURCE_RADIUS_RE = re.compile(
    r"(?:[\w-]*border-[\w-]*radius\s*:(?:[^;{}]|#\{[^}]*\})*"
    r"|\$[\w-]*radius[\w-]*\s*:(?:[^;{}]|#\{[^}]*\})*)"
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
    """Every surface renders Odoo CE's native radius; the cluster declares no override of its own."""

    def test_the_cluster_declares_no_radius_of_its_own(self):
        """No cluster source file declares a corner radius beyond ALLOWED_RADIUS_DECLARATIONS.

        The authored source is scanned rather than the compiled CSS: a rule that writes
        `border-radius` directly on a component never touches a Bootstrap token, so a compiled-CSS
        check would stay green while the surface is visibly rounder than core. Sass variables are
        scanned too. A failure names the file, the line and the declaration.
        """
        offenders = []
        scanned_modules = []
        skipped_dir_parts = (
            os.sep + "tests" + os.sep, os.sep + "lib" + os.sep, os.sep + "node_modules" + os.sep
        )
        for module in CLUSTER_MODULES:
            module_path = get_module_path(module, display_warning=False)
            if not module_path:
                continue
            scanned_modules.append(module)
            for root, _dirs, files in os.walk(module_path):
                for filename in sorted(files):
                    if not filename.endswith((".scss", ".css", ".xml", ".js")):
                        continue
                    absolute = os.path.join(root, filename)
                    relative = os.path.relpath(absolute, module_path).replace(os.sep, "/")
                    # tests own their fixtures; static/lib is vendored third-party code.
                    if any(part in absolute + os.sep for part in skipped_dir_parts):
                        continue
                    with open(absolute, "r", encoding="utf-8") as handle:
                        source = handle.read()
                    stripped = _strip_comments(source, filename)
                    permitted = ALLOWED_RADIUS_DECLARATIONS.get((module, relative), set())
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
            "renders Odoo CE's native radius, but %d declaration(s) were found beyond the "
            "allow-list:\n  %s\n\n"
            "Delete them - do NOT replace one override with another, and do not widen the "
            "allow-list unless the declaration is genuinely SHAPE-critical (a circle that would "
            "otherwise become a square) or is a new, deliberate, approved override, in which "
            "case add it to ALLOWED_RADIUS_DECLARATIONS with the reasoning, the way the 50%% "
            "skeleton avatar is handled."
            % (len(offenders), "\n  ".join(offenders)),
        )
