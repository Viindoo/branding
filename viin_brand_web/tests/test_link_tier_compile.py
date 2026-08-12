# Compiled-cascade guard for THE TEXT-LINK TIER (owner request 2026-08-03: "màu của text link ...
# tao muốn override nó thành màu secondary của Viindoo"). SSOT for everything named $link-* /
# --link-* in this cluster; the sibling tests/test_brand_color_compile.py deliberately no longer
# asserts a teal --link-color and points here instead (ODOO-AI-ETHOS #11).
#
# WHAT THE CHANGE ACTUALLY IS, AND WHY THE TEST HAS TWO HALVES
# =================================================================================================
# Odoo compiles Bootstrap with `$variable-prefix: ''`, so ONE unprefixed token - `--link-color` -
# carries two unrelated meanings: the HYPERLINK colour (the `a` reboot rule reads
# `--link-color-rgb`) and a generic "interactive accent" that three Bootstrap components borrow
# without being links (`$nav-link-color`, `$btn-link-color`, `$pagination-color`, all
# `var(--#{$prefix}link-color)` in web/static/lib/bootstrap/scss/_variables.scss). The owner asked
# for the first to be purple and was explicit that BUTTONS must stay teal, so
# static/src/scss/link_tier.scss SPLITS the token rather than re-pointing it.
#
# A one-sided test would therefore be worthless in both directions:
#   * asserting only "the link is purple" passes on a naive re-point that also turns the kanban
#     "Add Contact" .btn-link and every Bootstrap tab purple - the exact defect the owner named;
#   * asserting only "buttons are teal" passes on doing nothing at all.
# So every arm below asserts a PAIR: the hyperlink tier moved, and the borrower did not.
#
# WHY COMPILED CSS AND NOT THE SCSS SOURCE
# =================================================================================================
# "link_tier.scss contains $link-color: $o-brand-secondary" would stay green if the file lost its
# manifest anchor, if it landed AFTER Bootstrap's _variables.scss (making every assignment a no-op),
# or if core renamed a borrower variable. Only the compiled bundle shows whether the split reaches
# the pixel, so each assertion reads the value a real element resolves through the real cascade -
# and both bundles are compiled, because dark is an independent recompile in which the purple must
# NOT appear at all.
#
# THE DARK ARM IS AN INVERTED ASSERTION, ON PURPOSE
# =================================================================================================
# Under the COLOUR LAW's 2026-08-03 revision the brand purple is a LIGHT-MODE-ONLY accent. In
# web.assets_web_dark the link tier keeps the teal dark_palette.scss already sets, so the dark arm
# asserts the ABSENCE of purple and the PRESENCE of the unchanged dark teal. A future edit that
# "completes" the feature by giving the dark bundle a purple link reverses an owner decision and
# turns this red - read the COLOUR LAW block in static/src/scss/brand_variables.scss first.
import os
import re

from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    CHROME_BASE,
    DARK_BUNDLE,
    DARK_LINK_REF,
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _iter_rules,
    _normalize_colour,
)
# The brand-secondary purple lives only in SCSS (there is no Python constant for it, unlike the
# brand primary), so the expected value is READ from the module's own token SSOT with the resolver
# tests/test_brand_ssot.py owns, never re-literalised here.
from .test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
LINK_TIER_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "link_tier.scss")

# Backend surfaces a hyperlink actually renders on, and the AA threshold it must clear on each.
# White = the form sheet (where .o_form_uri many2one links live); #f8f9fa = --body-bg, the list /
# card surface; #e9ecef = --secondary-bg, the app band behind the home menu. Fixed design constants
# transcribed from the compiled palette, NOT recomputed from production Sass.
LINK_SURFACES = {
    "form sheet (white)": "#ffffff",
    "--body-bg list surface": "#f8f9fa",
    "--secondary-bg app band": "#e9ecef",
}

# The borrowers, as (human name, selector token the property is DECLARED on, custom property).
# Transcribed from web/static/lib/bootstrap/scss/. Note the first row: Bootstrap declares
# `--nav-link-color` on the CONTAINER `.nav` (_nav.scss:12) and only READS it on the item
# (`.nav-link { color: var(--nav-link-color) }`, :29), so the declaration is looked up on `.nav`.
# Getting that wrong is not academic - an earlier draft of this file queried `.nav-link`, found
# nothing, and reported a false "core renamed the token" failure. `.btn-link` (_buttons.scss:172)
# and `.pagination` do declare their own. Each is `var(--link-color)` in stock Bootstrap, which is
# precisely why they need re-anchoring once --link-color stops meaning "interactive teal".
LINK_BORROWERS = (
    ("Bootstrap tabs (--nav-link-color, declared on .nav)", ".nav", "--nav-link-color"),
    ("link-styled buttons (.btn-link)", ".btn-link", "--btn-color"),
    ("pagers (.pagination)", ".pagination", "--pagination-color"),
)


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


@tagged("post_install", "-at_install")
class TestLinkTierCompile(TransactionCase):
    """The hyperlink tier is the brand purple in light; nothing that is not a hyperlink follows it."""

    def _compiled_css(self, bundle_name):
        """Compile ``bundle_name`` and return its CSS payload (19.0 API:
        ``ir.qweb._get_asset_bundle(name, css=True, js=False).css()`` - the same contract the
        sibling compile tests use)."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so the link tier cannot be "
            "verified." % bundle_name,
        )
        self.assertNotIn(
            "a css error occured", css.lower(),
            "%s carries Odoo's CSS-error banner: on a Sass failure Odoo re-serves the PREVIOUS "
            "stylesheet instead of raising, so every assertion below would confirm the OLD colours. "
            "Fix the compile before reading this result." % bundle_name,
        )
        return css

    def _declared_on(self, css, selector_token, prop):
        """Every value declared for custom property ``prop`` on a rule whose selector list contains
        ``selector_token``, in source order (so the last entry is the winner at equal specificity).

        Matching is on a selector that IS or ENDS WITH the token as a whole compound - `.btn-link`
        matches `.btn-link` and `.o_foo .btn-link` but never `.btn-link-custom` - so a same-named
        unrelated component cannot smuggle a false pass in."""
        pattern = re.compile(r"(?:^|[\s>+~]|\A)%s(?:[:.\[]|$)" % re.escape(selector_token))
        needle = re.compile(r"%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = []
        for _order, selector, body in _iter_rules(css):
            if not pattern.search(selector):
                continue
            for match in needle.finditer(body):
                values.append(match.group(1).strip().lower())
        return values

    def _root_values(self, css, prop):
        """Every value declared for ``prop`` on a ``:root`` rule, in source order."""
        return self._declared_on(css, ":root", prop)

    def _expected_purple(self):
        purple = _resolve_scss_hex(_read(BRAND_VARIABLES_SCSS), "$o-brand-secondary")
        self.assertIsNotNone(
            purple,
            "$o-brand-secondary must be declared in static/src/scss/brand_variables.scss - it is "
            "the SSOT for every brand-secondary surface, the text link now included.",
        )
        return purple.lower()

    # ---------------------------------------------------------------------------------------------
    # LIGHT: the hyperlink tier moved to the brand purple
    # ---------------------------------------------------------------------------------------------
    def test_light_link_tokens_compile_to_the_brand_secondary(self):
        """:root --link-color / -rgb / --link-hover-color must carry the brand purple in light mode.

        These four tokens are what the `a` reboot rule reads
        (web/static/lib/bootstrap/scss/_reboot.scss:244 `color: rgba(var(--link-color-rgb), ...)`,
        with :hover swapping in --link-hover-color-rgb), so asserting them IS asserting the rendered
        hyperlink colour. The -rgb triplet is derived by parsing the SAME SSOT hex, never by
        re-implementing a Sass conversion.

        RED before link_tier.scss: all four compiled to the AA teal #007f8e / #005963."""
        expected_purple = self._expected_purple()
        css = self._compiled_css(BACKEND_BUNDLE)

        link_values = self._root_values(css, "--link-color")
        self.assertTrue(link_values, "no --link-color custom property found on :root.")
        self.assertIn(
            expected_purple, link_values,
            "--link-color must compile to the Viindoo secondary %s - the owner's 2026-08-03 text-link "
            "decision. Got %r (the AA teal %s means link_tier.scss did not take effect: check its "
            "manifest anchor is still BEFORE web/static/lib/bootstrap/scss/_variables.scss)."
            % (expected_purple, link_values, CHROME_BASE),
        )

        channels = expected_purple.lstrip("#")
        expected_rgb = "%d,%d,%d" % (
            int(channels[0:2], 16), int(channels[2:4], 16), int(channels[4:6], 16),
        )
        rgb_values = [
            re.sub(r"\s+", "", value) for value in self._root_values(css, "--link-color-rgb")
        ]
        self.assertTrue(rgb_values, "no --link-color-rgb custom property found on :root.")
        self.assertIn(
            expected_rgb, rgb_values,
            "--link-color-rgb must compile to the brand-secondary channels %s (%r). This is the "
            "token the `a` reboot rule actually reads, so a stale triplet means links still render "
            "the old hue even when --link-color looks right." % (expected_rgb, rgb_values),
        )

        # The hover rung must be a DARKER purple - Bootstrap's own shade of the same token, so no
        # second literal enters the module. Asserted as a relationship (same hue family, darker,
        # still AA on white) rather than as a hardcoded hex, so re-tuning the shade percentage is
        # not a false failure while a revert to teal - or a hover LIGHTER than the resting colour -
        # still is.
        hover_values = [
            _normalize_colour(value) for value in self._root_values(css, "--link-hover-color")
        ]
        hover_values = [value for value in hover_values if value]
        self.assertTrue(hover_values, "no --link-hover-color custom property found on :root.")
        hover = hover_values[-1]
        red, green, blue = (int(hover[i:i + 2], 16) for i in (1, 3, 5))
        self.assertGreater(
            blue, green,
            "--link-hover-color %s is not in the purple family (a purple has more blue than green); "
            "the hover rung must be derived from $o-brand-secondary, not left on the teal tier."
            % hover,
        )
        self.assertGreater(
            _contrast_ratio(hover, "#ffffff"), _contrast_ratio(expected_purple, "#ffffff"),
            "--link-hover-color %s must be DARKER than the resting link %s on a light surface - "
            "hover has to read as a state change." % (hover, expected_purple),
        )

    def test_light_link_purple_clears_wcag_aa_on_every_backend_surface(self):
        """The link purple must clear WCAG AA normal text on each surface a link renders on.

        Body text is the whole point of a link colour, so 4.5:1 (SC 1.4.3) is the bar - not the 3:1
        non-text threshold. Measured with the W3C luminance formula the cluster already owns; a
        future re-tuning of $o-brand-secondary that looks nicer but drops below AA turns this red."""
        expected_purple = self._expected_purple()
        for name, surface in LINK_SURFACES.items():
            ratio = _contrast_ratio(expected_purple, surface)
            self.assertGreaterEqual(
                round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                "the text-link purple %s measures only %.2f:1 on the %s (%s) - below the WCAG AA "
                "normal-text threshold %.1f:1."
                % (expected_purple, ratio, name, surface, WCAG_AA_NORMAL_TEXT),
            )

    # ---------------------------------------------------------------------------------------------
    # LIGHT: nothing that is NOT a hyperlink follows it
    # ---------------------------------------------------------------------------------------------
    def test_light_buttons_tabs_and_pagers_keep_the_interactive_teal(self):
        """The three Bootstrap components that BORROW the link token must stay on the AA teal.

        This is the owner's explicit constraint ("buttons must stay teal/neutral") and the reason
        the fix is a split rather than a re-point. Each borrower is asserted on the custom property
        Bootstrap declares for it, so the check survives a core restyle of the component itself.

        RED on a naive `$link-color: $o-brand-secondary` with no re-anchoring: all three inherit
        `var(--link-color)` and compile purple."""
        expected_purple = self._expected_purple()
        css = self._compiled_css(BACKEND_BUNDLE)
        for name, selector, prop in LINK_BORROWERS:
            values = self._declared_on(css, selector, prop)
            self.assertTrue(
                values,
                "no %s custom property found on %s - core renamed the token, so the re-anchor in "
                "link_tier.scss no longer reaches %s and it is silently free to follow the purple "
                "link tier. Re-ground against the current Bootstrap _variables.scss."
                % (prop, selector, name),
            )
            resolved = [_normalize_colour(value) for value in values]
            self.assertIn(
                CHROME_BASE, resolved,
                "%s must keep the interactive teal %s on %s; compiled %r. Under the COLOUR LAW "
                "teal = ACT, and a tab / link-styled button / pager is not a hyperlink."
                % (name, CHROME_BASE, prop, values),
            )
            self.assertNotIn(
                expected_purple, resolved,
                "%s picked up the text-link purple %s on %s (%r) - the split in link_tier.scss is "
                "not holding." % (name, expected_purple, prop, values),
            )

    def test_light_plain_buttons_are_untouched_by_the_link_tier(self):
        """`<a class="btn ...">` must render as a BUTTON, never as a purple link.

        Bootstrap's `.btn` declares its own `--btn-color` and paints `color: var(--btn-color)` at
        specificity (0,1,0), which beats the `a` reboot rule's (0,0,1) - so a link rendered as a
        button is already immune by construction. This asserts that construction still holds
        (rather than assuming it): the base `.btn` colour must be the body-text token, and must not
        be the link purple."""
        expected_purple = self._expected_purple()
        css = self._compiled_css(BACKEND_BUNDLE)
        values = self._declared_on(css, ".btn", "--btn-color")
        self.assertTrue(values, "no --btn-color custom property found on .btn.")
        base = values[0]
        self.assertNotIn(
            expected_purple, [_normalize_colour(value) for value in values[:1]],
            "the base .btn --btn-color compiled to the link purple (%r) - every `<a class=\"btn\">` "
            "in the backend would render as a link." % base,
        )
        self.assertIn(
            "body-color", base,
            "the base .btn --btn-color should still resolve through the body-text token (got %r); "
            "if core changed that, re-ground this assertion rather than deleting it." % base,
        )

    # ---------------------------------------------------------------------------------------------
    # DARK: the purple never enters the dark bundle
    # ---------------------------------------------------------------------------------------------
    def test_dark_link_tier_keeps_the_teal_and_never_goes_purple(self):
        """In web.assets_web_dark the link tier is UNCHANGED - the brand purple is light-only.

        Two assertions, and the negative one is the load-bearing half: the dark link token must not
        be the brand purple (2.50:1 on the dark panel - the measured defect that made the owner rule
        purple out of dark mode in the first place), and it must still be the readable dark teal
        dark_palette.scss sets. The teal is asserted by MEASURED contrast as well as by value, so a
        different AA-passing dark teal would still pass while a silent recompile of the light purple
        into dark could not."""
        expected_purple = self._expected_purple()
        css = self._compiled_css(DARK_BUNDLE)

        link_values = [_normalize_colour(value) for value in self._root_values(css, "--link-color")]
        link_values = [value for value in link_values if value]
        self.assertTrue(link_values, "no --link-color custom property found on :root in the dark bundle.")
        dark_link = link_values[-1]
        self.assertNotEqual(
            dark_link, expected_purple,
            "the dark bundle's --link-color compiled to the brand purple %s. The purple is a "
            "LIGHT-MODE-ONLY accent (COLOUR LAW, brand_variables.scss): link_tier.scss must keep "
            "its light arm behind the $o-viin-dark-bundle flag." % expected_purple,
        )
        self.assertEqual(
            dark_link, DARK_LINK_REF,
            "the dark bundle's --link-color must stay the owner-confirmed dark teal %s that "
            "dark_palette.scss:158 sets; got %s. The text-link change must not have touched dark "
            "at all." % (DARK_LINK_REF, dark_link),
        )
        ratio = _contrast_ratio(dark_link, "#111b1e")
        self.assertGreaterEqual(
            round(ratio, 2), WCAG_AA_NORMAL_TEXT,
            "the dark link colour %s measures only %.2f:1 on the dark panel #111b1e - below WCAG AA."
            % (dark_link, ratio),
        )

    def test_dark_borrowers_track_the_dark_teal_not_the_light_one(self):
        """The re-anchored borrowers must be SCHEME-AWARE, not frozen at the light teal.

        The re-anchor swapped a runtime `var(--link-color)` (which flipped per scheme for free) for
        a Sass value resolved per BUNDLE. That is only equivalent if the Sass token itself is
        scheme-split - so this asserts the dark bundle compiles them to the DARK teal. Pinning them
        to the light #007f8e would be a real regression: 3.69:1 on the dark panel, below AA."""
        css = self._compiled_css(DARK_BUNDLE)
        for name, selector, prop in LINK_BORROWERS:
            values = [
                _normalize_colour(value) for value in self._declared_on(css, selector, prop)
            ]
            values = [value for value in values if value]
            self.assertTrue(values, "no %s found on %s in the dark bundle." % (prop, selector))
            self.assertIn(
                DARK_LINK_REF, values,
                "%s must compile to the DARK interactive teal %s in web.assets_web_dark; got %r. "
                "The light teal %s is only 3.69:1 on the dark panel."
                % (name, DARK_LINK_REF, values, CHROME_BASE),
            )

    # ---------------------------------------------------------------------------------------------
    # Source-level invariants the compiled CSS cannot express
    # ---------------------------------------------------------------------------------------------
    def test_link_tier_introduces_no_new_hex_literal(self):
        """link_tier.scss must derive every colour from an existing token - no new brand hex.

        A cluster rule (tests/test_asset_upgrade.py enforces the sibling case in
        brand_variables.scss): a second nearly-identical literal is how a palette drifts out of
        SSOT. Every value in this file has to come from $o-brand-secondary / $o-main-link-color, or
        from Bootstrap's own shade formula applied to one of them."""
        source = _read(LINK_TIER_SCSS)
        # Comments document the recovered core values (#007F8E, #4FD4E2, ...) - those are prose, not
        # declarations, so only real code lines are scanned.
        code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
        code = re.sub(r"//[^\n]*", "", code)
        hexes = re.findall(r"#[0-9A-Fa-f]{3,8}\b", code)
        self.assertFalse(
            hexes,
            "link_tier.scss declares raw hex literal(s) %r. Derive from $o-brand-secondary / "
            "$o-main-link-color instead - the cluster keeps exactly one declaration per brand "
            "colour." % hexes,
        )
