import os
import re

from odoo.modules.module import get_module_path
from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
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

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_SRC = os.path.join(MODULE_DIR, "static", "src")
EDITOR_FONT_SCSS = os.path.join(STATIC_SRC, "scss", "editor_content_font.scss")

BUNDLES = (BACKEND_BUNDLE, DARK_BUNDLE)

# A selector frame is theme-owned when it names one of the module's own classes; the theme prefixes
# every class it authors with `o_viin_`, so this token is the ownership test.
THEME_CLASS_PREFIX = "o_viin_"

TEMPLATE_SUFFIXES = (".xml",)

_SCSS_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# home_menu.xml: `.o_viin_home_menu` > `.o_viin_home_content` > `.o_viin_home_header` >
# `<h1 class="o_viin_home_greeting">`. The greeting reads `$o-headings-font-family` by name
# (home_menu.scss), so it proves the brand heading font reaches the backend.
GREETING_CLASSES = frozenset({"o_viin_home_greeting"})
GREETING_ANCESTORS = HOME_MENU_ROOT_ANCESTORS | HOME_MENU_ROOT_CLASSES | {
    "o_viin_home_content", "o_viin_home_header", "d-flex", "flex-column",
}
# The brand heading face is asserted by name, not as a whole stack: the fallback tail is covered by
# the font-fallback test.
BRAND_HEADING_FONT = "Montserrat"


def _resolve_custom_property(css, name, hops=4):
    """Read a CSS custom property out of compiled CSS, following ``var()`` indirection.

    Bootstrap publishes the body stack as ``--body-font-family: #{inspect($font-family-base)}``
    while ``$font-family-base`` defaults to ``var(--font-sans-serif)``, which holds the literal list
    (lib/bootstrap/scss/_root.scss). The chain is followed from the property ``body`` reads rather
    than hardcoding the link that currently holds the list. Odoo compiles Bootstrap with an empty
    variable prefix, so the properties are unprefixed.

    :param name: the custom property to start from, e.g. ``--body-font-family``
    :param hops: how many ``var()`` references to follow
    :return: the first resolved value that is not a bare ``var()`` reference, or ``None`` when the
        property is absent or the chain does not terminate within ``hops``
    """
    custom_property_re = r"--%s\s*:\s*([^;}]+)"
    var_reference_re = re.compile(r"^var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)$")
    seen = set()
    current = name
    for _ in range(hops):
        if current in seen:
            return None
        seen.add(current)
        match = re.search(custom_property_re % re.escape(current.lstrip("-")), css)
        if not match:
            return None
        value = match.group(1).strip()
        reference = var_reference_re.match(value)
        if not reference:
            return value
        current = reference.group(1)
    return None


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_comments(text, filename):
    """Drop comments so a declaration is never matched inside prose."""
    text = _BLOCK_COMMENT_RE.sub("", text)
    if filename.endswith(TEMPLATE_SUFFIXES):
        return _XML_COMMENT_RE.sub("", text)
    return _SCSS_LINE_COMMENT_RE.sub("", text)


def _iter_declarations_with_scope(scss):
    """Walk a comment-stripped SCSS source and yield each declaration with its nesting.

    A brace-depth walk instead of a SCSS parser dependency: the only structure that matters is
    which selector frames a declaration sits inside. ``@if`` / ``@media`` frames are pushed like any
    other frame and never match the ownership test on their own, since they do not change which
    element a rule targets.

    :return: a generator of ``(selector_stack, property_line, line_number)``
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
    """The theme may not change the text core renders.

    ``text-transform`` changes what ``element.textContent`` looks like without touching the DOM, so
    every consumer of rendered text (core's HOOT assertions, ``:contains()`` tour triggers, a screen
    reader, copy/paste) reads a different string than the application produced. The rule is
    ownership: every ``text-transform`` this module declares is scoped under a selector the theme
    owns (an ``o_viin_*`` class), because those are the only elements whose text the theme authored.
    Static source guards need no database, so a violation is reported in seconds with a line number.
    """

    def _authored_sources(self, suffixes):
        for root, _dirs, files in os.walk(STATIC_SRC):
            for filename in sorted(files):
                if filename.endswith(suffixes):
                    yield os.path.join(root, filename), filename

    def test_every_text_transform_is_scoped_to_a_theme_owned_element(self):
        """The theme may case-transform its own labels; it may never case-transform core's text.

        The theme-owned sites (``.o_viin_home_section_label``, ``.o_viin_appearance_group``) pass
        unchanged. A surface that needs a case transform gets an ``o_viin_*`` class and the rule is
        scoped under it.
        """
        text_transform_decl_re = re.compile(r"(?:^|[;{\s])text-transform\s*:\s*([^;}]+)")
        offenders = []
        for path, filename in self._authored_sources((".scss", ".css")):
            scss = _strip_comments(_read(path), filename)
            for selector_stack, declaration, line in _iter_declarations_with_scope(scss):
                match = text_transform_decl_re.search(";%s" % declaration)
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
        """`.text-uppercase` and its siblings are the same defect as a ``text-transform`` rule.

        The theme's templates are ``t-inherit`` extensions of core templates, so a
        ``position="attributes"`` adding a case utility would transform a core element's text and
        pass a guard that reads only stylesheets. The scope is ``static/src`` (production markup); a
        tour may assert on such a class.
        """
        case_utility_re = re.compile(r"\btext-(uppercase|lowercase|capitalize)\b")
        offenders = []
        for path, filename in self._authored_sources(TEMPLATE_SUFFIXES):
            markup = _strip_comments(_read(path), filename)
            for match in case_utility_re.finditer(markup):
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
    """Compiled-CSS guards - what the browser receives, in both bundles."""

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
        """No rule reaching a command-palette or list-view hook declares `text-transform`.

        The source scan proves the theme authors none; this proves none arrives through a selector
        shape the scan attributes to no file, the dark bundle's independent recompile or a
        dependency. The hook list is short and named because the compiled CSS contains core's own
        rules, which legitimately declare ``text-transform`` elsewhere (ribbon, calendar, report
        tables).
        """
        core_text_hooks = (
            "o_command_category",
            "o_command_name",
            "o_command_palette_listbox",
            "o_list_table",
            "o_column_sortable",
            "o_list_renderer",
        )
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            offenders = []
            for _order, selector, body in _iter_rules(css):
                if not any(hook in selector for hook in core_text_hooks):
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
        """The brand heading font stays in the backend while the rich-text editor is scoped out of it.

        ``$o-headings-font-family`` feeds core's ``$headings-font-family`` and so every backend
        ``h1..h6``, and the theme's ``.o_viin_home_greeting`` reads it by name. Dropping the override
        or writing the editor reset broadly enough to reach the greeting loses Montserrat from the
        backend. Montserrat and Roboto are the Viindoo brand SSOT.
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
                "brand heading face %r. The brand font is scoped out of the RICH-TEXT EDITOR only; "
                "the backend keeps Montserrat." % (family, bundle_name, BRAND_HEADING_FONT),
            )

    def test_both_font_stacks_keep_odoos_unicode_and_emoji_fallback(self):
        """Neither the body nor the heading stack loses the fallback core gives every font list.

        Without the fallback tail an emoji in a record name, or a Vietnamese glyph the system face
        does not cover, renders as an empty box. ``o-add-unicode-support-font()`` splices Odoo's own
        Noto subset in before the generic family, and four emoji families keep emoji visible; they
        are different fallbacks, so both are measured, each emoji family individually. Both stacks
        are read from the compiled bundles (``web.assets_web_dark`` is an independent recompile), so
        the guard measures what a browser is handed.
        """
        unicode_support_font = "Odoo Unicode Support Noto"
        emoji_fallback_fonts = (
            "Apple Color Emoji",
            "Segoe UI Emoji",
            "Segoe UI Symbol",
            "Noto Color Emoji",
        )
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
                "`--font-sans-serif` (lib/bootstrap/scss/_root.scss); if core changed that "
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
                    unicode_support_font,
                    stack,
                    "In %s, %s does not name %r:\n  %s\nThat is Odoo's own fallback face for "
                    "characters a user's system font lacks or renders unreadably, and it is spliced "
                    "in by `o-add-unicode-support-font()` - which this declaration must go through, "
                    "exactly as core's own does (web/static/src/scss/primary_variables.scss, "
                    "$o-font-family-sans-serif / $o-headings-font-family)."
                    % (bundle_name, description, unicode_support_font, stack),
                )
                for emoji_font in emoji_fallback_fonts:
                    self.assertIn(
                        emoji_font,
                        stack,
                        "In %s, %s does not name %r:\n  %s\nWithout the emoji families an emoji in "
                        "backend text renders as an empty box."
                        % (bundle_name, description, emoji_font, stack),
                    )

    def test_command_rows_do_not_inherit_the_category_labels_typography(self):
        """The palette's command rows render at core's own size - no label rule leaks onto them.

        Core renders ``.o_command_category`` as the wrapper div holding every command row of a
        category, and puts the label in its first-child ``<span>``
        (web/static/src/core/commands/command_palette.xml), which already carries core's own
        ``text-uppercase fw-bold text-muted smaller`` utilities. A typography rule written against
        the wrapper inherits onto ``.o_command``, ``.o_command_name`` and ``.o_command_hotkey``, so
        any rule for the category label must target the label element, never the wrapper.
        """
        inheriting = {"font-size", "font-weight", "letter-spacing", "text-transform", "color"}
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            offenders = []
            for _order, selector, body in _iter_rules(css):
                # Rules whose last compound targets the wrapper itself (nothing after it).
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
    """An outgoing email body is not inlined with the brand heading font."""

    def test_the_editor_heading_reset_still_matches_cores_own_declaration(self):
        """The editor-scoped heading font stays a pointer to core's stack, not a stale copy.

        The theme overrides ``$o-headings-font-family`` without ``!default`` and loads it
        ``('before', ...)``, so core's own declaration is unreachable from any theme file and the
        editor reset re-states core's expression. ``mail``'s ``convert_inline`` writes the computed
        heading font into the saved mail body, so a drifted copy hands recipients a font they do not
        have. The core declaration is read from the installed ``web`` module, so the check follows
        whatever checkout is on the addons path.
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
            "core does not declare `$o-headings-font-family` in %s. The editor reset in %s exists "
            "to reproduce that value; re-ground both together." % (core_primary, EDITOR_FONT_SCSS),
        )
        expected = " ".join(core_decl.group(1).split())

        self.assertTrue(
            os.path.exists(EDITOR_FONT_SCSS),
            "%s is missing. It is what keeps the Viindoo brand heading font out of an outgoing email "
            "body." % EDITOR_FONT_SCSS,
        )
        theme = _strip_comments(_read(EDITOR_FONT_SCSS), "editor_content_font.scss")
        theme_decl = re.search(
            r"\$o-viin-editor-headings-font-family\s*:\s*(.+?)\s*;", theme, re.DOTALL
        )
        self.assertIsNotNone(
            theme_decl,
            "%s does not declare `$o-viin-editor-headings-font-family`, the variable that carries "
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
