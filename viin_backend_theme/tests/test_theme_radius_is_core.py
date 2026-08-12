# The cluster owns exactly ONE deliberate corner-radius override - owner decision D5's square-corners
# token - and ZERO others; every other surface renders Odoo CE's native radius.
#
# THE BEHAVIOUR UNDER GUARD (owner revision 2026-08-03, "viec override bo tron dang duoc dien ra o
# nhieu cho, hay ra soat ky de bo het" - the radius overriding is happening in many places, audit
# thoroughly and remove them all). The theme used to raise the whole Bootstrap radius map
# ($border-radius 0.5rem / -sm 0.375rem / -lg 0.75rem, the "D13" scale) and then re-inject that
# inflated value into a dozen individual components. The owner asked for all of it gone, so the rule
# this file protects is a CLUSTER-WIDE INVARIANT, not a single value:
#
#   (A) the compiled radius TOKENS equal core's, so every Bootstrap surface inherits Odoo CE's scale -
#       except the BASE-routed tokens, which equal the D5 override instead (square corners, base rung
#       only; -sm/-lg are untouched and still equal core's scale exactly);
#   (B) each component that Bootstrap routes through a runtime radius property resolves to that same
#       expected value (D5's override for base, core's own scale for -sm/-lg), so no file re-points
#       one of them behind the tokens' back;
#   (C) no source file in the cluster declares a radius at all, except the pinned shape-critical
#       circles and the single D5 base-rung token, so the invariant cannot be reopened by a SECOND,
#       undocumented override.
#
# OWNER DECISION D5 (square corners, base rung only). viin_brand_web's D4 restore
# (static/src/scss/brand_variables.scss:351, `$o-border-radius: 0 !default;`) put back a pre-19
# brand-identity token that a prior SCSS restructure had silently dropped. This file's ORIGINAL
# invariant (2026-08-03, "bo het") predates that restore and read any `$o-border-radius` assignment
# as exactly the regression it was written to catch - the two directly contradicted each other. The
# owner has since ruled D5: the restore is correct and stays, so THIS FILE's invariant is what
# updates - a single, SSOT-pinned base-rung exception, tracked dynamically (never hardcoded) so it
# cannot silently drift from its own source line. -sm / -lg are NOT part of D5 and still must equal
# core's own scale exactly, as before.
#
# WHY ALL THREE, AND WHY (C) IS NOT REDUNDANT. (A) and (B) only see properties Bootstrap itself
# emits. A rule like `.o_kanban_record { border-radius: 0.5rem }` writes the property DIRECTLY on a
# component and is invisible to both - which is exactly how the previous pass' audit list grew to a
# dozen files. (C) is the only assertion that catches it, and it is the one that turns RED the moment
# anyone re-adds a radius anywhere in the cluster outside the pinned D5 line and the shape-critical
# circles. Conversely (C) alone would pass if the D13 Sass scale came back through a *core* variable
# name in a file this scan cannot attribute, so (A)/(B) hold the compiled side. Together they are
# two-sided.
#
# WHY COMPILED CSS AND NOT ONLY THE SASS SOURCE, for (A)/(B). The observable is what the bundle
# emits. Bootstrap 5.3 gives most components no radius value of their own - it forwards the global
# one as a runtime custom property (e.g. `$dropdown-border-radius: var(--#{$prefix}border-radius)`,
# lib/bootstrap/scss/_variables.scss:1246) and Odoo sets `$variable-prefix: ''` - so a component can
# silently follow a raised global with nobody having written a component rule. Only the compiled
# value shows what a surface actually renders. BOTH bundles are checked: web.assets_web_dark is a
# full RECOMPILE (viin_brand_web/static/src/scss/dark_palette.scss), so it can drift on its own.
#
# THE EXPECTED VALUES: CORE'S OWN SCALE FOR -sm/-lg, THE CLUSTER'S D5 OVERRIDE FOR base - BOTH READ
# FROM THEIR SOURCE, NEVER HARDCODED. `$o-border-radius-sm` / `-lg` stay `o-to-rem(3px|6px)` in
# web/static/src/scss/primary_variables.scss:219-220 and are what core's own
# bootstrap_overridden.scss:100-101 feeds `$border-radius-sm` / `-lg` with; they are parsed out of
# that core file at test time. The BASE rung is different under D5: viin_brand_web's own
# brand_variables.scss:351 (`$o-border-radius: 0 !default;`) is now base's ground truth, so this
# guard reads IT dynamically too, instead of hardcoding "0" - if the owner ever retunes the D5 value,
# this test and the source-scan's exact-pin (below) both move together instead of silently diverging.
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
#
# OWNER DECISION D5 IS PINNED THE SAME WAY, BUT IS NOT A SHAPE EXCEPTION. The circles above survive
# because the radius IS the element's identity; D5 (`$o-border-radius: 0 !default;`,
# viin_brand_web/static/src/scss/brand_variables.scss:351) survives for a DIFFERENT reason - it is
# a deliberate Viindoo brand-identity choice (square corners) the owner ruled affirmatively KEEPS,
# not a rounding taste this file exists to police. It is pinned with the same EXACT (path,
# declaration) discipline - a single base-rung Sass token, not a broad allow - so a SECOND radius
# declaration anywhere else in the cluster still fails and gets an explicit decision, same as a
# fourth circle would.
import os
import re

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_open

# Both compiled bundles: the backend, and the dark bundle (a full recompile, so it can drift alone).
BUNDLES = ("web.assets_backend", "web.assets_web_dark")

# web/static/src/scss/primary_variables.scss - the Odoo radius scale core's Bootstrap map reads.
CORE_RADIUS_SOURCE = "web/static/src/scss/primary_variables.scss"
# ... and the file that proves core still FEEDS $border-radius* from that scale, so an Odoo change
# that decouples them makes this guard RED rather than silently vacuous.
CORE_BOOTSTRAP_SOURCE = "web/static/src/scss/bootstrap_overridden.scss"

# Owner decision D5's single base-rung override (square corners) - the ONE line this file's
# invariant now excludes from "the cluster owns no radius". Read dynamically (never hardcoded) so a
# future D5 retune keeps this guard and the source-scan allow-list below in sync with each other.
CLUSTER_OVERRIDE_SOURCE = ("viin_brand_web", "static/src/scss/brand_variables.scss")
# `$o-border-radius: <value> !default;` - the same declaration the allow-list entry below pins.
_CLUSTER_OVERRIDE_RE = re.compile(r"\$o-border-radius:\s*([^;!]+?)\s*!default")

# `$o-border-radius: o-to-rem(4px) !default;` -> the px operand. o-to-rem() is core's own px->rem
# helper (web/static/src/scss/functions.scss:30), which divides by a fixed 16.
_CORE_SCALE_RE = {
    "base": re.compile(r"\$o-border-radius:\s*o-to-rem\(\s*(\d+(?:\.\d+)?)px\s*\)"),
    "sm": re.compile(r"\$o-border-radius-sm:\s*o-to-rem\(\s*(\d+(?:\.\d+)?)px\s*\)"),
    "lg": re.compile(r"\$o-border-radius-lg:\s*o-to-rem\(\s*(\d+(?:\.\d+)?)px\s*\)"),
}
_ROOT_FONT_SIZE_PX = 16.0

# Which core token each compiled custom property must resolve to. Grounded per property, not assumed:
#   --border-radius / -sm / -lg  core bootstrap_overridden.scss:99-101 ($o-border-radius*)
#   --modal-border-radius        core bootstrap_overridden.scss:265 ($modal-content-border-radius: $border-radius)
#   --popover-border-radius      core bootstrap_overridden.scss:243 ($popover-border-radius: $border-radius)
#   --dropdown-border-radius     Bootstrap _variables.scss:1246 (var(--border-radius))
#   --tooltip-border-radius      Bootstrap _variables.scss:1408 (var(--border-radius))
#   --card-border-radius         Bootstrap _variables.scss (var(--border-radius))
#   --badge / --alert            Bootstrap _variables.scss (var(--border-radius))
EXPECTED_TOKEN = {
    "--border-radius": "base",
    "--border-radius-sm": "sm",
    "--border-radius-lg": "lg",
    "--card-border-radius": "base",
    "--modal-border-radius": "base",
    "--dropdown-border-radius": "base",
    "--popover-border-radius": "base",
    "--tooltip-border-radius": "base",
    "--badge-border-radius": "base",
    "--alert-border-radius": "base",
}

# `.btn` is the property the owner complained about first and is a special case: Bootstrap emits the
# SAME `--btn-border-radius` name from three rules (.btn / .btn-sm / .btn-lg) with three different
# source values, so the assertion is on the resolved SET. Core's expectation: the base and -lg sizes
# sit on the base token (core pins `$btn-border-radius-lg: $border-radius`, bootstrap_overridden.scss:176)
# and -sm on the small one - i.e. nothing outside core's own scale.
BTN_RADIUS_PROPERTY = "--btn-border-radius"
BTN_EXPECTED_TOKENS = {"base", "sm"}

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
    # OWNER DECISION D5 (square corners, base rung only): the ONE deliberate radius declaration this
    # cluster now ships. `$o-border-radius: 0 !default;` restores a pre-19 brand-identity token (D4)
    # the owner has ruled KEEPS - it is a single SSOT-pinned base-rung Sass token, not a component
    # override, and not a reopening of the dozen-file "bo het" regression this file's header
    # describes: -sm / -lg stay untouched, and this is the ONLY entry pinned to this file, so a
    # second declaration added here tomorrow still fails and gets its own explicit decision.
    ("viin_brand_web", "static/src/scss/brand_variables.scss"): {"$o-border-radius:0!default"},
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

# A custom-property declaration, anchored so `--border-radius` never matches inside
# `--btn-border-radius` or `--Attachment-Image-border-radius`.
_LENGTH_RE = re.compile(r"^(-?\d*\.?\d+)(rem|px)$")
# A unitless zero is a valid CSS length and is what core actually emits for the un-rounded corners
# of a radius shorthand (`purchase/.../purchase_dashboard.scss:5`: `#{$r} #{$r} 0 0`). It carries no
# unit, so `_LENGTH_RE` cannot match it - without this the shorthand branch of `_resolve` reads a
# CORE shape as unparseable (that is what kept runbot 223607 red).
_ZERO_RE = re.compile(r"^-?0*\.?0+$")
_VAR_HOP_RE = re.compile(r"^var\(\s*(--border-radius(?:-sm|-lg)?)\s*\)$")


def _declaration_re(prop):
    return re.compile(r"(?<![-\w])" + re.escape(prop) + r"\s*:\s*([^;}]+)")


def _strip_comments(text, path):
    text = _BLOCK_COMMENT_RE.sub("", text)
    if path.endswith(".xml"):
        return _XML_COMMENT_RE.sub("", text)
    return _SCSS_LINE_COMMENT_RE.sub("", text)


@tagged("post_install", "-at_install")
class TestThemeRadiusIsCore(TransactionCase):
    """Every surface renders Odoo CE's native radius, except the single D5 square-corners token.

    OWNER DECISION D5: the cluster deliberately keeps ONE base-rung radius override (square
    corners); -sm/-lg and everything else stay on core's own scale. See the module header for the
    full D4-vs-original-invariant lineage.
    """

    # --- helpers -----------------------------------------------------------------------------

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so no radius can be verified."
            % bundle_name,
        )
        return css

    def _core_scale_rem(self):
        """Odoo CE's native radius scale, in rem, READ from core's own variable declarations."""
        with file_open(CORE_RADIUS_SOURCE, "r") as core_file:
            source = core_file.read()
        scale = {}
        for token, pattern in _CORE_SCALE_RE.items():
            match = pattern.search(source)
            self.assertIsNotNone(
                match,
                "%s no longer declares the `$o-border-radius%s: o-to-rem(<n>px)` token. That scale is "
                "what core's own bootstrap_overridden.scss feeds $border-radius* with, i.e. the "
                "definition of 'Odoo CE's native radius' - re-ground this guard against the new "
                "declaration rather than hardcoding a number."
                % (CORE_RADIUS_SOURCE, "" if token == "base" else "-" + token),
            )
            scale[token] = float(match.group(1)) / _ROOT_FONT_SIZE_PX
        return scale

    def _cluster_override_rem(self):
        """Owner decision D5's base-rung override, in rem, READ from its single source line.

        NOT HARDCODED, for the same reason `_core_scale_rem` above reads core dynamically: if the
        owner ever retunes `$o-border-radius`, this test and the source-scan's exact-pinned
        ALLOWED_RADIUS_DECLARATIONS entry both track the new value from the SAME line, so they
        cannot silently diverge from each other or from what the bundle actually compiles.
        """
        module, relative = CLUSTER_OVERRIDE_SOURCE
        module_path = get_module_path(module, display_warning=False)
        self.assertTrue(
            module_path,
            "%s is not on the addons path, so owner decision D5's square-corners override cannot be "
            "read. Re-ground CLUSTER_OVERRIDE_SOURCE on the cluster's real module layout."
            % (module,),
        )
        with open(os.path.join(module_path, relative), "r", encoding="utf-8") as handle:
            source = handle.read()
        # COMMENTS MUST BE STRIPPED FIRST. The header block right above the real declaration quotes
        # core's OWN `$o-border-radius: o-to-rem(4px) !default;` inside a `//` line for documentation
        # (brand_variables.scss:339) - an un-stripped search would match that quoted text first
        # (leftmost match wins) and silently read D5's value as core's 4px instead of the cluster's
        # actual override. Same reasoning as `_strip_comments`'s other caller, the source-scan below.
        stripped = _strip_comments(source, relative)
        match = _CLUSTER_OVERRIDE_RE.search(stripped)
        self.assertIsNotNone(
            match,
            "%s/%s no longer declares `$o-border-radius: <value> !default;`. Owner decision D5 "
            "(square corners, base rung only) depends on this single token as the base rung's "
            "ground truth - re-ground this guard against the new declaration rather than assuming "
            "the override is still there." % (module, relative),
        )
        value = self._plain_length(match.group(1))
        self.assertIsNotNone(
            value,
            "%s/%s declares `$o-border-radius: %s !default;`, and %r is not a plain length this "
            "guard can parse - follow the new shape here rather than hardcoding D5's value."
            % (module, relative, match.group(1), match.group(1)),
        )
        return value

    @staticmethod
    def _plain_length(raw):
        value = raw.strip().lower()
        if _ZERO_RE.match(value):
            return 0.0
        match = _LENGTH_RE.match(value)
        if not match:
            return None
        magnitude = float(match.group(1))
        return magnitude if match.group(2) == "rem" else magnitude / _ROOT_FONT_SIZE_PX

    def _bundle_scale(self, css, bundle_name):
        """The radius scale THIS bundle actually compiled - what a var() passthrough resolves to.

        WHY THE BUNDLE'S OWN NUMBERS AND NOT CORE'S. Bootstrap forwards most component radii as
        `var(--border-radius)`, so a passthrough is the CORRECT post-fix shape and the guard has to
        follow it. But following it into CORE's expected number would make every passthrough
        consumer compare core against core and pass no matter what the global actually compiled -
        the silently-vacuous guard this file exists to avoid. (Not hypothetical: an earlier draft
        did exactly that and stayed green with `$border-radius: 0.5rem` restored.) Resolving against
        the bundle's own `:root` values means an inflated global propagates into every consumer's
        assertion, which is how the real cascade behaves.
        """
        scale = {}
        for token, prop in (("base", "--border-radius"), ("sm", "--border-radius-sm"),
                            ("lg", "--border-radius-lg")):
            values = [m.group(1) for m in _declaration_re(prop).finditer(css)]
            self.assertTrue(
                values,
                "Nothing declares %s in the compiled %s. Bootstrap emits the whole radius scale from "
                "`:root` (lib/bootstrap/scss/_root.scss), so its absence means the scale changed "
                "shape - re-ground this guard." % (prop, bundle_name),
            )
            length = self._plain_length(values[-1])
            self.assertIsNotNone(
                length,
                "%s compiled to %r in %s rather than a plain length. The root scale is the anchor "
                "every other radius resolves against, so it cannot itself be an indirection - "
                "follow the new hop here rather than deleting the assertion."
                % (prop, values[-1], bundle_name),
            )
            scale[token] = length
        return scale

    def _resolve(self, raw, bundle_scale):
        """Resolve a compiled radius value to rem, following at most one var(--border-radius*) hop.

        MULTI-VALUE SHORTHANDS are resolved per corner and reduced to their LARGEST rounding.
        CSS `border-radius` (and the `--btn-border-radius` token Bootstrap feeds it) accepts up to
        four lengths, and CORE legitimately uses that to round only some corners - e.g.
        `purchase/static/src/views/purchase_dashboard.scss:5,9` emits
        `--btn-border-radius: <r> <r> 0 0` / `0 0 <r> <r>` for the stacked dashboard buttons. A
        single-value-only reader returns None there and fails the guard for a CORE shape rather than
        a cluster regression (that is exactly how runbot build 223607 went red - the shorthand only
        appears once `purchase` is installed, which the narrow local module set never did).
        Every component still has to resolve to core's scale or to an explicit 0, so an inflated
        radius in ANY corner keeps failing - the guard loses no teeth, only the false positive.
        """
        parts = raw.strip().split()
        if len(parts) > 1:
            resolved = [self._resolve(part, bundle_scale) for part in parts]
            if any(value is None for value in resolved):
                return None
            # 0 corners carry no rounding to compare; the guard is about the rounded ones.
            rounded = [value for value in resolved if value]
            return max(rounded) if rounded else 0.0
        hop = _VAR_HOP_RE.match(raw.strip())
        if hop:
            return bundle_scale[{"--border-radius": "base", "--border-radius-sm": "sm",
                                 "--border-radius-lg": "lg"}[hop.group(1)]]
        return self._plain_length(raw)

    # --- (A) + (B): what the bundles actually compile ------------------------------------------

    def test_every_bootstrap_radius_property_compiles_to_odoo_ces_own_scale(self):
        """Radius tokens equal core's scale, EXCEPT base-routed ones, which equal D5's override.

        OWNER DECISION D5: the base rung is a deliberate square-corners exception (see module
        header); -sm / -lg are NOT part of D5 and stay pinned to core's own scale unchanged.

        RED BEFORE GREEN: with the theme's D13 scale in place (`$border-radius: 0.5rem` in a
        bootstrap_overridden.scss appended to web._assets_backend_helpers) `:root` compiled
        --border-radius 0.5rem against the D5-expected 0rem, and every card / input / modal /
        dropdown / popover / tooltip / alert / badge inherited it. Restoring that file turns this
        RED and the message names each property and its rem delta. A base-routed property compiling
        to anything other than the D5 value, or a sm/lg-routed property drifting from core's scale,
        both stay RED - this test's teeth are unchanged, only WHAT base compares against changed.

        THE LEVER IS ASSERTED TOO, NOT JUST THE VALUES. If core ever stops feeding $border-radius
        from $o-border-radius, comparing the bundle against $o-border-radius would be comparing
        against a variable nothing reads - green and meaningless. Asserting core still wires them
        together makes that a RED test instead of a silently vacuous one.
        """
        with file_open(CORE_BOOTSTRAP_SOURCE, "r") as core_bootstrap:
            core_bootstrap_source = core_bootstrap.read()
        self.assertIn(
            "$border-radius: $o-border-radius", core_bootstrap_source,
            "%s no longer feeds $border-radius from $o-border-radius, so this guard's expected value "
            "is read from a token core has stopped using. Re-ground it on core's new wiring."
            % CORE_BOOTSTRAP_SOURCE,
        )

        scale = self._core_scale_rem()
        # D5: the base rung's expected value is the cluster's own override, not core's raw scale.
        # -sm / -lg are untouched and keep expecting core's scale exactly, as before D5.
        expected = dict(scale)
        expected["base"] = self._cluster_override_rem()
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            bundle_scale = self._bundle_scale(css, bundle_name)
            for prop, token in EXPECTED_TOKEN.items():
                values = [m.group(1) for m in _declaration_re(prop).finditer(css)]
                self.assertTrue(
                    values,
                    "Nothing declares %s in the compiled %s. Bootstrap emits it from the radius map, "
                    "so its absence means the map changed shape - re-ground this guard rather than "
                    "dropping the property." % (prop, bundle_name),
                )
                for raw in values:
                    actual = self._resolve(raw, bundle_scale)
                    self.assertIsNotNone(
                        actual,
                        "%s compiled to %r in %s - neither a plain length nor a "
                        "var(--border-radius*) passthrough. Some file introduced a new indirection; "
                        "follow the new hop here rather than deleting the assertion."
                        % (prop, raw, bundle_name),
                    )
                    if token == "base":
                        source_note = "owner decision D5's square-corners override"
                        source_ref = "%s in %s/%s" % (
                            "$o-border-radius", CLUSTER_OVERRIDE_SOURCE[0], CLUSTER_OVERRIDE_SOURCE[1],
                        )
                    else:
                        source_note = "Odoo CE's own value"
                        source_ref = "$o-border-radius-%s in %s" % (token, CORE_RADIUS_SOURCE)
                    self.assertAlmostEqual(
                        actual, expected[token], places=4,
                        msg="%s compiles %.4frem in %s but %s for it is %.4frem (%s). Except for "
                            "the single D5 base-rung exception, the cluster ships ZERO radius "
                            "overrides (owner 2026-08-03) - find the file that re-declares this and "
                            "delete the declaration, do not re-pin it to another value."
                            % (prop, actual, bundle_name, source_note, expected[token], source_ref),
                    )

    def test_buttons_render_odoo_ces_native_radius(self):
        """`.btn` / `.btn-sm` / `.btn-lg` corners are exactly {D5 override, core's small} - nothing else.

        OWNER DECISION D5: buttons are the surface the owner originally complained about, and under
        D5 the base rung's expected value is now the cluster's own square-corners override rather
        than core's raw scale; `sm` is NOT part of D5 and still expects core's own small radius
        unchanged. Kept as its own test because Bootstrap emits the SAME property name from three
        rules (.btn / .btn-sm / .btn-lg) with three different source values - a shape the generic
        per-property assertion above cannot express. The resolved SET must be exactly {D5 override,
        core's small}: D5's override for `.btn` and (via core's own
        `$btn-border-radius-lg: $border-radius` pin) `.btn-lg`, core's small for `.btn-sm`. A button
        radius compiling to anything OUTSIDE that two-value set still fails.

        WOULD FAIL IF REVERTED: re-raising the global puts every one of the three on the D13 value,
        outside the allowed set, and this reports the exact rem delta per size."""
        scale = self._core_scale_rem()
        # D5: "base" resolves to the cluster's own override; "sm" is untouched, still core's scale.
        expected_values = dict(scale)
        expected_values["base"] = self._cluster_override_rem()
        allowed = {round(expected_values[token], 4) for token in BTN_EXPECTED_TOKENS}
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            bundle_scale = self._bundle_scale(css, bundle_name)
            values = [m.group(1) for m in _declaration_re(BTN_RADIUS_PROPERTY).finditer(css)]
            self.assertTrue(
                values,
                "Nothing declares %s in the compiled %s, so button corners are no longer routed "
                "through it - re-ground this guard on Bootstrap's new lever."
                % (BTN_RADIUS_PROPERTY, bundle_name),
            )
            for raw in values:
                actual = self._resolve(raw, bundle_scale)
                self.assertIsNotNone(
                    actual,
                    "%s compiled to %r in %s - neither a plain length nor a var(--border-radius*) "
                    "passthrough." % (BTN_RADIUS_PROPERTY, raw, bundle_name),
                )
                self.assertIn(
                    round(actual, 4), allowed,
                    "A button compiles a %.4frem corner radius in %s; the allowed set is %s rem "
                    "(owner decision D5's square-corners override %.4f / Odoo CE's own small radius "
                    "%.4f, $o-border-radius-sm in %s). The owner asked for D5's radius on the base "
                    "rung and core's radius on the small rung - remove whatever raises it outside "
                    "this set instead of re-pinning."
                    % (actual, bundle_name, sorted(allowed), expected_values["base"],
                       expected_values["sm"], CORE_RADIUS_SOURCE),
                )

    # --- (C): the cluster authors no radius at all ---------------------------------------------

    def test_the_cluster_declares_no_radius_of_its_own(self):
        """No cluster source file declares a corner radius, except the shape-critical circles and
        owner decision D5's single square-corners token.

        OWNER DECISION D5: `$o-border-radius: 0 !default;` (viin_brand_web/static/src/scss/
        brand_variables.scss:351) is pinned in ALLOWED_RADIUS_DECLARATIONS by its EXACT normalized
        text, the same discipline as the shape-critical circles - not a reopening of the sweep below,
        and not a loosened rule: any OTHER radius declaration anywhere in the cluster still fails.

        THE ASSERTION THE COMPILED ONES CANNOT MAKE. A rule that writes `border-radius` DIRECTLY on a
        component (`.o_kanban_record`, `.o_loading_indicator`, the retired `999px` pills, the home
        menu tiles) never touches a Bootstrap token, so the bundle-level guards above stay green
        while the surface is visibly rounder than core. That is precisely how the override count grew
        to a dozen files before the owner asked for a sweep. This scan is the only thing that keeps
        it at the D5-plus-circles baseline.

        SASS VARIABLES ARE SCANNED TOO, not just CSS declarations: the original D13 regression
        entered as `$border-radius: 0.5rem`, which emits no `border-radius:` text at all in the file
        that causes it. It is also how D5's own base-rung token is caught and pinned here.

        RED BEFORE GREEN: re-adding any single removed line - e.g. `border-radius: $border-radius` to
        views/kanban/kanban_record.scss - names the file, the line number and the declaration. A
        SECOND radius line added to brand_variables.scss (or a change to the D5 line's text that no
        longer matches the pinned exact string) goes RED the same way."""
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
            "The cluster is supposed to own exactly ONE corner-radius declaration - owner decision "
            "D5's square-corners token in %s - and ZERO others, so every other surface renders "
            "Odoo CE's native radius (owner revision 2026-08-03, 'bo het', narrowed by the later D5 "
            "ruling), but %d declaration(s) were found beyond the allow-list:\n  %s\n\nDelete them - "
            "do NOT replace one override with another, and do not widen the allow-list unless the "
            "declaration is genuinely SHAPE-critical (a circle that would otherwise become a square) "
            "or is itself owner decision D5, in which case add it to ALLOWED_RADIUS_DECLARATIONS "
            "with the reasoning, the way the 50%% skeleton avatar and the D5 token are handled."
            % ("/".join(CLUSTER_OVERRIDE_SOURCE), len(offenders), "\n  ".join(offenders)),
        )
