# A theme may restyle core, but it may NOT change the TEXT core renders.
#
# THE BEHAVIOUR UNDER GUARD, and why it is a behaviour and not a style preference.
# -----------------------------------------------------------------------------------------------
# `text-transform` is the one CSS property that changes what `element.textContent` LOOKS like
# without changing the DOM. Every automated oracle that reads rendered text - Odoo's own HOOT
# assertions, `:contains()` tour triggers, a screen reader, a user's copy/paste - therefore reads a
# DIFFERENT string than the application produced. That is not a look, it is a contract break, and it
# is measurable: on runbot batch 223955 two declarations in THIS module turned 100 core assertions
# red at once, e.g.
#
#     > Expected: [ "Command#", ]
#     > Received: [ "COMMAND#", ]
#
# (`@web/core/commands/command_palette`, log_404581.txt). The theme had written
# `text-transform: uppercase` on `.o_command_category` (web/static/src/core/commands/) and on
# `.o_list_table thead th` (web/static/src/views/list/) - both CORE elements rendering CORE strings.
#
# SO THE INVARIANT IS OWNERSHIP, NOT AN ALLOW-LIST OF VICTIMS. A guard phrased as "never uppercase
# `.o_command_category` or `thead th`" would have to grow a new line every time the theme reaches for
# a different core hook, and would be silent until it did. The rule this file enforces instead is:
#
#     every `text-transform` this module declares must be scoped under a selector the THEME owns
#     (a `.o_viin_*` class), because those are the only elements whose text the theme authored.
#
# Two sites are legitimately theme-owned today and are expected to keep passing:
#   * `home_menu.scss` `.o_viin_home_section_label` - the "APPLICATIONS" heading, our string;
#   * `appearance_systray/appearance_systray.scss` `.o_viin_appearance_group` - our systray group
#     label, our string.
# Neither is core text. Both stay allowed for free, with no exception list to maintain.
#
# WHY THE TEMPLATE SCAN IS PART OF THE SAME BEHAVIOUR. `text-transform` is not the only way to
# uppercase core text - Bootstrap ships `.text-uppercase` / `.text-lowercase` / `.text-capitalize`
# utilities, and a `position="attributes"` on an inherited core template can add one to an element
# the theme does not own. Guarding only the SCSS property would leave that door open while claiming
# the behaviour is protected, so the utility classes are scanned too.
#
# WHY A SOURCE SCAN AND ALSO COMPILED CSS. The source scan fails with a file and a line, needs no
# database, and sees a rule whose selector no cascade resolver could model. The compiled arm sees
# what a browser actually receives - including a rule that arrives through a core hook this scan
# attributes to nobody, or through the dark bundle's independent recompile. Neither half is
# redundant; both are cheap. This mirrors the two-sided shape of the sibling guards
# (test_theme_radius_is_core, test_theme_core_chrome_untouched).
#
# SECOND, UNRELATED-LOOKING GUARD IN THIS FILE, AND WHY IT BELONGS HERE. The same "do not change what
# core renders" rule covers the FONT the rich-text editor inlines into an outgoing email: the theme
# repoints `$o-headings-font-family` to the Viindoo brand stack, and `convert_inline` copies the
# COMPUTED heading font into the saved mail body, so a recipient's mail client is handed a font it
# does not have (owner decision D2, 2026-08-17). The theme therefore restores core's own stack inside
# `.odoo-editor-editable` / `.note-editable`, and the guard below pins that restoration to CORE's
# declaration - read out of the installed `web` module at test time, never transcribed - so a future
# core change fails a two-second unit test instead of a thirty-minute HOOT run.
import os
import re

from odoo.modules.module import get_module_path
from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    _declarations,
    _iter_rules,
    _winning_declaration,
)

from .test_theme_dark_widgets import (
    HOME_MENU_ROOT_CLASSES,
    HOME_MENU_ROOT_ANCESTORS,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
STATIC_SRC = os.path.join(MODULE_DIR, "static", "src")
EDITOR_FONT_SCSS = os.path.join(STATIC_SRC, "scss", "editor_content_font.scss")

BUNDLES = (BACKEND_BUNDLE, DARK_BUNDLE)

# A selector frame is theme-owned when it names one of the module's own classes. The theme prefixes
# every class it authors with `o_viin_` (Odoo SCSS guideline: `o_<module_name>` - the cluster's
# agreed short form), so this single token IS the ownership test.
THEME_CLASS_PREFIX = "o_viin_"

STYLE_SUFFIXES = (".scss", ".css")
TEMPLATE_SUFFIXES = (".xml",)

# Bootstrap's case utilities - the other way to change rendered text. `text-transform` and these are
# the complete set of levers; nothing else in CSS rewrites textContent's appearance.
_CASE_UTILITY_RE = re.compile(r"\btext-(uppercase|lowercase|capitalize)\b")
_TEXT_TRANSFORM_DECL_RE = re.compile(r"(?:^|[;{\s])text-transform\s*:\s*([^;}]+)")

_SCSS_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# The CORE hooks whose text this theme is known to have rewritten (runbot 223955 RC-2) plus their
# immediate neighbours, used by the COMPILED arm. Deliberately a small, named list: the compiled CSS
# contains core's own rules too, so a broad substring sweep there would report core's `.text-uppercase`
# utility and other legitimate core declarations. The SOURCE arm above is the exhaustive one.
CORE_TEXT_HOOKS = (
    "o_command_category",
    "o_command_name",
    "o_command_palette_listbox",
    "o_list_table",
    "o_column_sortable",
    "o_list_renderer",
)

# home_menu.xml - `.o_viin_home_menu` > `.o_viin_home_content` > `.o_viin_home_header` >
# `<h1 class="o_viin_home_greeting">`. The greeting is the theme's own most prominent heading and
# the one surface that reads `$o-headings-font-family` by NAME (home_menu.scss), so it is the
# element that proves the brand heading font survived the D2 work.
GREETING_CLASSES = frozenset({"o_viin_home_greeting"})
GREETING_ANCESTORS = HOME_MENU_ROOT_ANCESTORS | HOME_MENU_ROOT_CLASSES | {
    "o_viin_home_content", "o_viin_home_header", "d-flex", "flex-column",
}
# The brand heading face, read as a NAME rather than as a whole stack: the point is that Viindoo's
# heading font is still first, not that the fallback tail is byte-identical (the fallback is exactly
# what D2 changed, by restoring the Unicode/emoji tail).
BRAND_HEADING_FONT = "Montserrat"

# The two fallbacks every Odoo font stack is supposed to end with, and what each one is FOR.
# `o-add-unicode-support-font()` splices in Odoo's own small Noto subset just before the generic
# family, for characters the user's system font either lacks or renders unreadably
# (web/static/src/scss/utils.scss); the four emoji families are what keep an emoji from rendering as
# an empty box. They are DIFFERENT fallbacks - a stack can carry one and miss the other, and this
# theme managed to do exactly that on one line each - so both are measured.
UNICODE_SUPPORT_FONT = "Odoo Unicode Support Noto"
EMOJI_FALLBACK_FONTS = (
    "Apple Color Emoji",
    "Segoe UI Emoji",
    "Segoe UI Symbol",
    "Noto Color Emoji",
)
# Bootstrap publishes the BODY stack as a runtime custom property and `body` reads it from there.
# Odoo compiles Bootstrap with an EMPTY variable prefix (bootstrap_overridden.scss), so the property
# is unprefixed - but both spellings are accepted here so a prefix change fails as a clear "not
# found" rather than as a silent pass.
#
# AND IT IS PUBLISHED THROUGH AN INDIRECTION, which is worth stating because the first version of
# this guard missed it and failed on a value carrying no font names at all. Bootstrap emits
# `--body-font-family: #{inspect($font-family-base)}` (lib/bootstrap/scss/_root.scss:53) while
# `$font-family-base` itself defaults to `var(--font-sans-serif)`, and the LITERAL list lands in
# `--font-sans-serif` (_root.scss:44, fed from `$font-family-sans-serif`, which Odoo feeds from
# `$o-font-family-sans-serif` - bootstrap_overridden.scss:117). So the guard starts at the property
# `body` actually reads and FOLLOWS the chain, rather than hardcoding whichever link currently
# happens to hold the list. A chain it cannot resolve is reported, never skipped.
_FONT_CUSTOM_PROPERTY_RE = r"--%s\s*:\s*([^;}]+)"
_VAR_REFERENCE_RE = re.compile(r"^var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)$")
_MAX_VAR_HOPS = 4


def _resolve_custom_property(css, name, hops=_MAX_VAR_HOPS):
    """Read a CSS custom property out of compiled CSS, following `var()` indirection.

    Returns the first resolved value that is NOT itself a bare `var()` reference, or None when the
    property is absent or the chain does not terminate within `hops`.
    """
    seen = set()
    current = name
    for _ in range(hops):
        if current in seen:
            return None  # a cycle - report rather than spin
        seen.add(current)
        match = re.search(_FONT_CUSTOM_PROPERTY_RE % re.escape(current.lstrip("-")), css)
        if not match:
            return None
        value = match.group(1).strip()
        reference = _VAR_REFERENCE_RE.match(value)
        if not reference:
            return value
        current = reference.group(1)
    return None


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_comments(text, filename):
    """Drop comments so a declaration is never matched inside prose (these files document heavily)."""
    text = _BLOCK_COMMENT_RE.sub("", text)
    if filename.endswith(TEMPLATE_SUFFIXES):
        return _XML_COMMENT_RE.sub("", text)
    return _SCSS_LINE_COMMENT_RE.sub("", text)


def _iter_declarations_with_scope(scss):
    """Yield ``(selector_stack, property_line, line_number)`` for every declaration in a SCSS source.

    A hand-rolled walk rather than a SCSS parser dependency: the only structure that matters here is
    "which selector frames am I nested inside", which brace depth answers exactly. `@if` / `@media`
    frames are pushed like any other frame and simply never match the ownership test on their own -
    which is correct, since an `@if` does not change WHICH element a rule targets, only whether it is
    emitted. The input must already be comment-stripped.
    """
    stack = []
    buffer = ""
    line = 1
    for char in scss:
        if char == "\n":
            line += 1
        if char == "{":
            stack.append(" ".join(buffer.split()))
            buffer = ""
        elif char == "}":
            if buffer.strip():
                yield tuple(stack), buffer.strip(), line
            buffer = ""
            if stack:
                stack.pop()
        elif char == ";":
            if buffer.strip():
                yield tuple(stack), buffer.strip(), line
            buffer = ""
        else:
            buffer += char


def _is_theme_owned(selector_stack):
    """True when some frame in the nesting chain names a class this module authored."""
    return any(THEME_CLASS_PREFIX in frame for frame in selector_stack)


@tagged("post_install", "-at_install")
class TestThemeAuthorsNoCoreTextTransform(BaseCase):
    """Static source guards - no DB needed, so a violation is reported in seconds with a line number."""

    def _authored_sources(self, suffixes):
        for root, _dirs, files in os.walk(STATIC_SRC):
            for filename in sorted(files):
                if filename.endswith(suffixes):
                    yield os.path.join(root, filename), filename

    def test_every_text_transform_is_scoped_to_a_theme_owned_element(self):
        """The theme may case-transform ITS OWN labels; it may never case-transform core's text.

        RED ON THE PRE-FIX TREE, and this is the whole point of the file: before the 2026-08-17 fix
        this reported exactly two offenders -
          static/src/core/commands/command_palette.scss  `.o_command_palette .o_command_category`
          static/src/views/list/list_renderer.scss       `.o_list_renderer .o_list_table thead th`
        - the two declarations that broke 100 core HOOT assertions on runbot batch 223955. The two
        theme-owned sites (`.o_viin_home_section_label`, `.o_viin_appearance_group`) pass unchanged,
        which is what makes this a rule about OWNERSHIP rather than a blanket ban.

        If a future theme surface genuinely needs a case transform, give the element a `.o_viin_*`
        class and scope the rule under it - that is not a workaround, it is the rule: the theme owns
        the elements it names, and only those.
        """
        offenders = []
        for path, filename in self._authored_sources(STYLE_SUFFIXES):
            scss = _strip_comments(_read(path), filename)
            for selector_stack, declaration, line in _iter_declarations_with_scope(scss):
                match = _TEXT_TRANSFORM_DECL_RE.search(";%s" % declaration)
                if not match or _is_theme_owned(selector_stack):
                    continue
                offenders.append(
                    "%s (near line %d): `text-transform: %s` under %r - none of those selectors "
                    "is a `%s*` class, so this rewrites text the theme did not author."
                    % (
                        os.path.relpath(path, MODULE_DIR),
                        line,
                        match.group(1).strip(),
                        " ".join(selector_stack) or "<file root>",
                        THEME_CLASS_PREFIX,
                    )
                )
        self.assertFalse(
            offenders,
            "This theme case-transforms text it does not own, in %d place(s):\n  %s\n\nEvery "
            "automated oracle that reads rendered text - core's own HOOT assertions, `:contains()` "
            "tour triggers, a screen reader, a user's copy/paste - then reads a different string "
            "than the application produced. Delete the declaration, or move it onto a `%s*` element "
            "the theme actually owns." % (len(offenders), "\n  ".join(offenders), THEME_CLASS_PREFIX),
        )

    def test_the_theme_adds_no_bootstrap_case_utility_to_core_markup(self):
        """`.text-uppercase` & friends are the same defect wearing a class name.

        The theme's templates are `t-inherit` extensions of CORE templates, so a
        `position="attributes"` adding `text-uppercase` would uppercase a core element's text exactly
        as the SCSS rule did - and would sail past a guard that only reads stylesheets. Scoped to
        `static/src` (production markup): a tour may legitimately assert on such a class.
        """
        offenders = []
        for path, filename in self._authored_sources(TEMPLATE_SUFFIXES):
            markup = _strip_comments(_read(path), filename)
            for match in _CASE_UTILITY_RE.finditer(markup):
                line = markup.count("\n", 0, match.start()) + 1
                offenders.append(
                    "%s (near line %d of the comment-stripped file): `text-%s`"
                    % (os.path.relpath(path, MODULE_DIR), line, match.group(1))
                )
        self.assertFalse(
            offenders,
            "The theme puts a Bootstrap case utility on template markup, in %d place(s):\n  %s\n\n"
            "These templates inherit CORE templates, so the utility lands on an element whose text "
            "core produced - the same contract break as a `text-transform` declaration."
            % (len(offenders), "\n  ".join(offenders)),
        )


@tagged("post_install", "-at_install")
class TestCoreTextRendersUntransformed(TransactionCase):
    """Compiled-CSS guards - what the browser actually receives, in BOTH bundles."""

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so nothing here is verified."
            % bundle_name,
        )
        return css

    def test_no_compiled_rule_case_transforms_a_core_command_or_list_element(self):
        """No rule reaching a command-palette or list-view hook may declare `text-transform`.

        The source scan above proves the THEME authors none. This proves none ARRIVES - through a
        selector shape the scan attributes to no file, through the dark bundle's independent
        recompile (viin_brand_web/static/src/scss/dark_palette.scss rebuilds the whole cascade), or
        through a dependency of ours.

        The hook list is deliberately short and named: compiled CSS contains core's own rules, and
        core legitimately ships `.text-uppercase` and a handful of `text-transform` declarations of
        its own (ribbon, calendar, mobile settings, report tables) that have nothing to do with
        these surfaces. Widening this to every core class would report those and be deleted within a
        week - the SOURCE arm is the exhaustive half.
        """
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            offenders = []
            for _order, selector, body in _iter_rules(css):
                if not any(hook in selector for hook in CORE_TEXT_HOOKS):
                    continue
                if THEME_CLASS_PREFIX in selector:
                    continue  # a theme-owned element that merely lives inside a core container
                for value, _important in _declarations(body, {"text-transform"}):
                    offenders.append("%s { text-transform: %s }" % (selector, value.strip()))
            self.assertFalse(
                offenders,
                "In %s, %d compiled rule(s) case-transform text rendered by core's command palette "
                "or list view:\n  %s\n\nCore reads those strings back in its own assertions - e.g. "
                "`@web/core/commands/command_palette` expects \"Command#\" and receives "
                "\"COMMAND#\"." % (bundle_name, len(offenders), "\n  ".join(offenders)),
            )

    def test_the_home_menu_greeting_still_renders_in_the_brand_heading_font(self):
        """D2 scoped the brand heading font OUT of the editor - it must still be IN the backend.

        This is the blast-radius half of owner decision D2. `$o-headings-font-family` feeds core's
        `bootstrap_overridden.scss:133` -> `$headings-font-family` -> every backend `h1..h6`, AND the
        theme's own `.o_viin_home_greeting` reads it by name (home_menu.scss). Two mistakes would be
        invisible without this test: dropping the override "to fix the mail font" (Montserrat gone
        from the whole backend), or writing the editor reset broadly enough to reach the greeting.
        Asserting the FONT NAME rather than the whole stack is deliberate - D2 legitimately changed
        the fallback tail (that is the Unicode/emoji restore), and pinning the tail here would just
        duplicate the drift guard below.

        Montserrat and Roboto are the Viindoo brand SSOT and are explicitly not up for revert.
        """
        greeting = {
            "classes": GREETING_CLASSES,
            "ancestors": GREETING_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            family = _winning_declaration(css, greeting, ("font-family",))
            self.assertIsNotNone(
                family,
                "No compiled `font-family` applies to the home-menu greeting "
                "(.o_viin_home_greeting) in %s - the brand heading typography is gone from the "
                "backend." % bundle_name,
            )
            self.assertIn(
                BRAND_HEADING_FONT,
                family,
                "The home-menu greeting compiles `font-family: %s` in %s, which does not name the "
                "brand heading face %r. D2 scoped the brand font out of the RICH-TEXT EDITOR only; "
                "the backend keeps Montserrat exactly as before." % (family, bundle_name, BRAND_HEADING_FONT),
            )

    def test_both_font_stacks_keep_odoos_unicode_and_emoji_fallback(self):
        """Neither the body nor the heading stack may lose the fallback core gives every font list.

        THE OBSERVABLE IS WHAT THE USER SEES, not what the SCSS says. An emoji in a record name, a
        heading with a Vietnamese glyph the system face happens not to cover - those render as empty
        boxes when the tail of the font stack is missing, and nothing else in the suite notices.
        This theme replaced BOTH of core's declarations and dropped a fallback from each: the
        headings line lost the four emoji families outright, and both lines lost the
        `o-add-unicode-support-font()` wrapper that splices in Odoo's own Noto subset.

        Both stacks are read out of the COMPILED bundle rather than the source, so the guard measures
        the value a browser is actually handed - it survives a refactor that moves the declaration,
        and it catches a stack that is correct in Sass but mangled by the cascade. Both bundles are
        checked because web.assets_web_dark is an independent recompile.

        RED ON REVERT, either side: drop the wrapper from `$o-font-family-sans-serif` and the body
        stack loses the UNICODE_SUPPORT_FONT subset; drop it from `$o-headings-font-family` and the
        greeting does. Delete the emoji names from either list and that list fails on the emoji
        assertion instead. The four emoji families are asserted individually so a partial revert
        cannot slip through.
        """
        greeting = {
            "classes": GREETING_CLASSES,
            "ancestors": GREETING_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)

            body_stack = _resolve_custom_property(css, "--body-font-family")
            self.assertIsNotNone(
                body_stack,
                "%s publishes no resolvable `--body-font-family`, so the backend body font cannot "
                "be verified. Bootstrap emits it from $font-family-base, which normally forwards to "
                "`--font-sans-serif` (lib/bootstrap/scss/_root.scss:44,53); if core changed that "
                "chain, re-ground this guard rather than deleting it." % bundle_name,
            )
            stacks = {
                "the backend BODY font ($o-font-family-sans-serif)": body_stack,
                "the backend HEADING font ($o-headings-font-family)": _winning_declaration(
                    css, greeting, ("font-family",)
                ),
            }
            for description, stack in stacks.items():
                self.assertIsNotNone(
                    stack,
                    "No compiled font stack resolves for %s in %s." % (description, bundle_name),
                )
                self.assertIn(
                    UNICODE_SUPPORT_FONT,
                    stack,
                    "In %s, %s does not name %r:\n  %s\nThat is Odoo's own fallback face for "
                    "characters a user's system font lacks or renders unreadably, and it is spliced "
                    "in by `o-add-unicode-support-font()` - which this declaration must go through, "
                    "exactly as core's own does (web/static/src/scss/primary_variables.scss:114,117)."
                    % (bundle_name, description, UNICODE_SUPPORT_FONT, stack),
                )
                for emoji_font in EMOJI_FALLBACK_FONTS:
                    self.assertIn(
                        emoji_font,
                        stack,
                        "In %s, %s does not name %r:\n  %s\nWithout the emoji families an emoji in "
                        "backend text renders as an empty box."
                        % (bundle_name, description, emoji_font, stack),
                    )

    def test_command_rows_do_not_inherit_the_category_labels_typography(self):
        """The palette's command ROWS render at core's own size - the label rule may not leak onto them.

        `.o_command_category` is NOT the category label. Core renders it as the WRAPPER div that
        holds every command row of that category, and puts the label in its first-child `<span>`
        (web/static/src/core/commands/command_palette.xml:25-26, where the span already carries core's
        own `text-uppercase fw-bold text-muted smaller` utilities). A rule written against the wrapper
        therefore INHERITS onto `.o_command`, `.o_command_name` and `.o_command_hotkey` - which is why
        the palette's rows rendered at 11px, muted, bold and letter-spaced. That is a defect a user
        SEES, independent of any test.

        So the guard is about the SELECTOR's reach: any typography rule this cluster writes for the
        category label must target the label element, never the wrapper that also contains the rows.
        """
        inheriting = {"font-size", "font-weight", "letter-spacing", "text-transform", "color"}
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            offenders = []
            for _order, selector, body in _iter_rules(css):
                # Rules whose LAST compound targets the wrapper itself (no descendant/child after it).
                for part in selector.split(","):
                    part = part.strip()
                    if not part.endswith(".o_command_category"):
                        continue
                    for prop in sorted(inheriting):
                        for value, _important in _declarations(body, {prop}):
                            offenders.append("%s { %s: %s }" % (part, prop, value.strip()))
            self.assertFalse(
                offenders,
                "In %s, %d declaration(s) target the command-palette category WRAPPER "
                "(`.o_command_category`) with an inheritable typography property:\n  %s\n\nEvery one "
                "of them cascades onto the command rows inside it. Target the label span "
                "(`.o_command_category > span`) instead - core's template puts the label there."
                % (bundle_name, len(offenders), "\n  ".join(offenders)),
            )


@tagged("post_install", "-at_install")
class TestEditorContentKeepsCoresPortableFont(BaseCase):
    """Owner decision D2: an outgoing email body may not be inlined with the brand heading font."""

    def test_the_editor_heading_reset_still_matches_cores_own_declaration(self):
        """The editor-scoped heading font must stay a POINTER to core's stack, not a stale copy.

        WHY THIS EXISTS. `$o-headings-font-family` is overridden by this theme without `!default` and
        loaded `('before', ...)`, so core's own declaration no-ops and its value is unreachable from
        any theme file. The editor reset therefore has to re-state core's expression - and a re-stated
        value is a copy, and a copy rots. `mail`'s `convert_inline` writes the COMPUTED heading font
        into the saved mail body, so when it rots the only thing that notices is
        `@mail/inline/html_mail_field` inside a thirty-minute HOOT run.

        This test closes that loop in two seconds: it reads core's real declaration out of the
        INSTALLED `web` module (`get_module_path`, so it follows whatever checkout is on the addons
        path) and asserts the theme's reset still names the same font list. If core re-tunes its
        heading stack, this fails first and says so.
        """
        core_primary = os.path.join(
            get_module_path("web"), "static", "src", "scss", "primary_variables.scss"
        )
        self.assertTrue(
            os.path.exists(core_primary),
            "core's web/static/src/scss/primary_variables.scss was not found at %s - re-ground this "
            "guard on core's new layout rather than deleting it." % core_primary,
        )
        core_decl = re.search(
            r"^\$o-headings-font-family\s*:\s*(.+?)\s*!default\s*;",
            _read(core_primary),
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(
            core_decl,
            "core no longer declares `$o-headings-font-family` in %s. The editor reset in %s exists "
            "to reproduce that value; re-ground both together." % (core_primary, EDITOR_FONT_SCSS),
        )
        expected = " ".join(core_decl.group(1).split())

        self.assertTrue(
            os.path.exists(EDITOR_FONT_SCSS),
            "%s is missing. It is what keeps the Viindoo brand heading font out of an outgoing email "
            "body (owner decision D2, 2026-08-17)." % EDITOR_FONT_SCSS,
        )
        theme = _strip_comments(_read(EDITOR_FONT_SCSS), "editor_content_font.scss")
        theme_decl = re.search(
            r"\$o-viin-editor-headings-font-family\s*:\s*(.+?)\s*;", theme, re.DOTALL
        )
        self.assertIsNotNone(
            theme_decl,
            "%s no longer declares `$o-viin-editor-headings-font-family`, the variable that carries "
            "core's portable system font stack into the rich-text editor." % EDITOR_FONT_SCSS,
        )
        self.assertEqual(
            " ".join(theme_decl.group(1).split()),
            expected,
            "The editor's heading font has DRIFTED from core's own stack.\n  core (%s): %s\n  theme "
            "(%s): %s\nThe reset exists so a mail body is inlined with fonts every recipient has - "
            "core's system stack is exactly that list, so it must be copied verbatim. `mail`'s "
            "convert_inline writes the computed value into the saved body, and "
            "`@mail/inline/html_mail_field` asserts it character for character."
            % (
                core_primary,
                expected,
                EDITOR_FONT_SCSS,
                " ".join(theme_decl.group(1).split()),
            ),
        )
