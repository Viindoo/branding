# Compiled-cascade guard for the text-link tier: the hyperlink colour is the Viindoo brand purple
# in light mode and its light tone in dark, and the link-styled controls share it. SSOT for everything named
# $link-* / --link-* in this cluster.
#
# Odoo compiles Bootstrap with `$variable-prefix: ''`, so ONE unprefixed token - `--link-color` -
# feeds the hyperlink colour (the `a` reboot rule reads `--link-color-rgb`) and three Bootstrap
# components that render as links (`$nav-link-color`, `$btn-link-color`, `$pagination-color`, all
# `var(--#{$prefix}link-color)` in web/static/lib/bootstrap/scss/_variables.scss).
# static/src/scss/link_tier.scss sets them per bundle from `$o-main-link-color`, so they follow
# the link colour of each scheme; a plain `.btn` keeps its own colour.
#
# The assertions read the compiled bundles, not the SCSS source: a source check stays green if
# the file loses its manifest anchor, lands after Bootstrap's _variables.scss (making every
# assignment a no-op) or core renames a borrower variable. Both bundles are compiled because dark
# is an independent recompile.
#
# In web.assets_web_dark the link tier takes the light purple dark_palette.scss sets, because the
# brand purple is only 2.50:1 on the dark panel (see the COLOUR LAW block in
# static/src/scss/brand_variables.scss).
import os
import re

from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    BRAND_PURPLE,
    DARK_BUNDLE,
    DARK_LINK_REF,
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _iter_rules,
    _normalize_colour,
)
# The link purple lives only in SCSS, so the expected value is read from brand_variables.scss with
# the resolver of tests/test_brand_ssot.py.
from .test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
LINK_TIER_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "link_tier.scss")

# Backend surfaces a hyperlink renders on. White = the view surface: form sheet, list cell, kanban
# card, dialog and popover (where .o_form_uri many2one links live); #f8f9fa = --body-bg, the app
# canvas under them (kanban canvas, chatter panel, dropdown menu); #e9ecef = --secondary-bg, the
# app band behind the home menu. Transcribed from the compiled palette, not recomputed from Sass.
LINK_SURFACES = {
    "form sheet (white)": "#ffffff",
    "--body-bg app canvas": "#f8f9fa",
    "--secondary-bg app band": "#e9ecef",
}

# The borrowers, as (human name, selector token the property is DECLARED on, custom property),
# from web/static/lib/bootstrap/scss/. Bootstrap declares `--nav-link-color` on the container
# `.nav` and only reads it on `.nav-link`, so the declaration is looked up on `.nav`; `.btn-link`
# and `.pagination` declare their own. Each is `var(--link-color)` in stock Bootstrap, which is
# why they need re-anchoring once --link-color is the brand link tone.
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
        """Compile ``bundle_name`` and return its CSS payload."""
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
            "%s carries Odoo's CSS-error banner: on a Sass failure Odoo re-serves the previous "
            "stylesheet instead of raising, so every assertion would confirm stale colours."
            % bundle_name,
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
        purple = _resolve_scss_hex(_read(BRAND_VARIABLES_SCSS), "$o-main-link-color")
        self.assertIsNotNone(
            purple,
            "$o-main-link-color must be declared in static/src/scss/brand_variables.scss - it is "
            "the SSOT of the text link.",
        )
        return purple.lower()

    def test_light_link_tokens_compile_to_the_brand_purple(self):
        """:root --link-color / -rgb / --link-hover-color must carry the brand purple in light mode.

        These four tokens are what the `a` reboot rule reads
        (web/static/lib/bootstrap/scss/_reboot.scss `color: rgba(var(--link-color-rgb), ...)`,
        with :hover swapping in --link-hover-color-rgb), so asserting them is asserting the rendered
        hyperlink colour. The -rgb triplet is derived by parsing the same SSOT hex."""
        expected_purple = self._expected_purple()
        css = self._compiled_css(BACKEND_BUNDLE)

        link_values = self._root_values(css, "--link-color")
        self.assertTrue(link_values, "no --link-color custom property found on :root.")
        self.assertIn(
            expected_purple, link_values,
            "--link-color must compile to the Viindoo link purple %s. Got %r (check that "
            "link_tier.scss manifest anchor is still BEFORE "
            "web/static/lib/bootstrap/scss/_variables.scss)."
            % (expected_purple, link_values),
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
            "--link-color-rgb must compile to the link-purple channels %s (%r). This is the "
            "token the `a` reboot rule actually reads, so a stale triplet means links still render "
            "the old hue even when --link-color looks right." % (expected_rgb, rgb_values),
        )

        # The hover rung must be a darker purple, Bootstrap's own shade of the same token. It is
        # asserted as a relationship (same hue family, darker) rather than a hex, so re-tuning the
        # shade percentage passes while a lighter hover fails.
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
            "the hover rung must be derived from $o-main-link-color."
            % hover,
        )
        self.assertGreater(
            _contrast_ratio(hover, "#ffffff"), _contrast_ratio(expected_purple, "#ffffff"),
            "--link-hover-color %s must be DARKER than the resting link %s on a light surface - "
            "hover has to read as a state change." % (hover, expected_purple),
        )

    def test_light_link_purple_clears_wcag_aa_on_every_backend_surface(self):
        """The link purple must clear WCAG AA normal text on each surface a link renders on.

        A link is body text, so the bar is 4.5:1 (SC 1.4.3), not the 3:1 non-text threshold."""
        expected_purple = self._expected_purple()
        for name, surface in LINK_SURFACES.items():
            ratio = _contrast_ratio(expected_purple, surface)
            self.assertGreaterEqual(
                round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                "the text-link purple %s measures only %.2f:1 on the %s (%s) - below the WCAG AA "
                "normal-text threshold %.1f:1."
                % (expected_purple, ratio, name, surface, WCAG_AA_NORMAL_TEXT),
            )

    def test_light_plain_buttons_are_untouched_by_the_link_tier(self):
        """`<a class="btn ...">` must render as a BUTTON, never as a purple link.

        Bootstrap's `.btn` declares its own `--btn-color` and paints `color: var(--btn-color)` at
        specificity (0,1,0), which beats the `a` reboot rule's (0,0,1), so a link rendered as a
        button is immune by construction. The base `.btn` colour must be the body-text token and
        not the link purple."""
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
            "the base .btn --btn-color should still resolve through the body-text token (got %r)."
            % base,
        )

    def test_dark_link_tier_takes_the_light_purple_not_the_brand_purple(self):
        """In web.assets_web_dark the link tier takes the light purple of dark_palette.scss.

        The dark link token must not be the brand purple (2.50:1 on the dark panel), and it must
        be the readable light purple, asserted by value and by measured contrast."""
        expected_purple = self._expected_purple()
        css = self._compiled_css(DARK_BUNDLE)

        link_values = [_normalize_colour(value) for value in self._root_values(css, "--link-color")]
        link_values = [value for value in link_values if value]
        self.assertTrue(link_values, "no --link-color custom property found on :root in the dark bundle.")
        dark_link = link_values[-1]
        self.assertNotEqual(
            dark_link, expected_purple,
            "the dark bundle's --link-color compiled to the brand purple %s, 2.50:1 on the dark "
            "panel: dark_palette.scss must set the light purple." % expected_purple,
        )
        self.assertEqual(
            dark_link, DARK_LINK_REF,
            "the dark bundle's --link-color must be the light purple %s that dark_palette.scss "
            "sets; got %s." % (DARK_LINK_REF, dark_link),
        )
        ratio = _contrast_ratio(dark_link, "#111b1e")
        self.assertGreaterEqual(
            round(ratio, 2), WCAG_AA_NORMAL_TEXT,
            "the dark link colour %s measures only %.2f:1 on the dark panel #111b1e - below WCAG AA."
            % (dark_link, ratio),
        )

    def test_dark_borrowers_track_the_dark_link_tone_not_the_light_one(self):
        """The link-styled controls must follow the dark link purple, not a light-scheme colour.

        The borrowers take a Sass value resolved per bundle rather than a runtime
        `var(--link-color)`, so the Sass token itself must be scheme-split; the dark bundle must
        compile them to the dark link purple. The light #7f4282 is 2.50:1 on the dark panel, below AA."""
        css = self._compiled_css(DARK_BUNDLE)
        for name, selector, prop in LINK_BORROWERS:
            values = [
                _normalize_colour(value) for value in self._declared_on(css, selector, prop)
            ]
            values = [value for value in values if value]
            self.assertTrue(values, "no %s found on %s in the dark bundle." % (prop, selector))
            self.assertIn(
                DARK_LINK_REF, values,
                "%s must compile to the DARK link purple %s in web.assets_web_dark; got %r. "
                "The light purple %s is only 2.50:1 on the dark panel."
                % (name, DARK_LINK_REF, values, BRAND_PURPLE),
            )

    def test_link_tier_introduces_no_new_hex_literal(self):
        """link_tier.scss must derive every colour from an existing token - no new brand hex.

        A second nearly-identical literal is how a palette drifts out of SSOT. Every value in this
        file has to come from $o-main-link-color, or from Bootstrap's own
        shade formula applied to one of them."""
        source = _read(LINK_TIER_SCSS)
        # Comments quote colour values; only code lines are scanned.
        code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
        code = re.sub(r"//[^\n]*", "", code)
        hexes = re.findall(r"#[0-9A-Fa-f]{3,8}\b", code)
        self.assertFalse(
            hexes,
            "link_tier.scss declares raw hex literal(s) %r. Derive from "
            "$o-main-link-color instead - the cluster keeps exactly one declaration per brand "
            "colour." % hexes,
        )
