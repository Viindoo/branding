# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): once `viin_brand_web` contributes its dark palette to
# `web.assets_backend_lazy_dark` (the bundle `web/static/src/views/view.js:348-352` loads whenever
# `cookie.get("color_scheme") === "dark"` before mounting a pivot or graph view -
# `web/__manifest__.py:144-146` declares it as a bare `('include', 'web.assets_backend_lazy')`
# today, carrying none of the brand's dark tokens), the pivot's own text must be readable against
# the dark panel, its header's HOVER state must read as a subtle tint rather than a hard swap, and
# the SIBLING light lazy bundle must compile exactly as it does today.
#
# WHY THIS BUNDLE, AND WHY COMPILED CSS: `web/static/src/views/pivot/pivot_view.scss` (core, read
# in full - it is not touched by this change) declares every colour under test via ONE Sass
# variable each - `$body-color` for the resting header/measure/value text
# (`@include o-hover-text-color($body-color, $headings-color)` and the enable_linking value-cell
# rule), `map-get($grays, "200")` for the hover band, and `$headings-color` for the hover label.
# `web.assets_backend_lazy` compiles ONLY variable-declaration partials plus `graph/**` and
# `pivot/**` (no `web/static/lib/bootstrap/scss/_root.scss`), so none of these ever reach the page
# as a `var()` custom property the way the always-loaded `web.assets_backend` bundle's tokens do -
# every value below bakes in as a LITERAL hex the moment the bundle compiles. That means the ONLY
# way to know what colour a pivot cell actually renders in this lazy bundle is to compile it and
# read the literal the cascade produced - a source-substring check on pivot_view.scss (core, not
# ours) would prove nothing about whether `dark_palette.scss` ever reaches this specific bundle.
#
# GROUNDING FOR THE LIGHT-BUNDLE VALUES BELOW - measured by compiling `web.assets_backend_lazy`
# via `ir.qweb._get_asset_bundle(..., css=True, js=False)` (the same compile-and-read method every
# test class in this file uses):
#   .o_pivot_measure_row / .o_pivot_origin_row / .o_pivot_header_cell_closed /
#   .o_pivot_header_cell_opened      resting color: #212529     hover color: #000000
#                                     hover background-color: #e9ecef !important
#   .o_pivot_cell_value:not(.o_empty) (enable_linking)  resting color: #212529
#                                                        hover/focus color: $o-main-link-color's
#                                                        own value (core's pivot_view.scss feeds
#                                                        this state directly from that variable -
#                                                        read live from brand_variables.scss below,
#                                                        never re-literalised here)
# These are asserted as the LIGHT bundle's unchanged baseline (non-regression) and as the value the
# DARK bundle's resting text must move AWAY from, onto the design's own literal dark answer
# (#EDF4F5 on #111B1E = 15.55:1 - DARK_READABLE_TEXT / DARK_BODY_BG, the same SSOT constants the
# rest of this cluster's compiled-cascade suite already uses) - never re-derived via a Sass
# darken()/mix() equivalent in Python.
import os

from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BODY_BG,
    DARK_READABLE_TEXT,
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _declarations,
    _iter_rules,
    _normalize_colour,
    dark_palette_var,
)
from .test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

PIVOT_LAZY_DARK_BUNDLE = "web.assets_backend_lazy_dark"
PIVOT_LAZY_LIGHT_BUNDLE = "web.assets_backend_lazy"

# Header / measure-row selectors that share ONE compiled rule per state in core's pivot_view.scss
# (transcribed above). Checked individually rather than assuming they always stay grouped, so a
# future split of that rule cannot silently drop one of the four from coverage.
_HEADER_SELECTORS = (
    ".o_pivot_measure_row",
    ".o_pivot_origin_row",
    ".o_pivot_header_cell_closed",
    ".o_pivot_header_cell_opened",
)
_VALUE_CELL_SELECTOR = ".o_pivot_cell_value:not(.o_empty)"

# "A subtle tint, not a hard swap" (design), asserted as an UPPER bound on how far the hover
# background may sit from the resting one - not a WCAG threshold (those are MINIMUMS), a design
# proximity bound of the cluster's own choosing.
HOVER_BAND_MAX_CONTRAST = 2.0


def _values_ending_with(css, suffix, prop):
    """Every ``prop`` value declared on a rule whose selector ends EXACTLY in ``suffix``.

    ``_iter_rules`` already yields one full compound selector per call (it splits the rule's
    comma-separated selector list itself), so a plain ``str.endswith`` is enough to tell the
    resting compound (``...o_pivot_header_cell_closed``) apart from its ``:hover``/``:focus``
    siblings - those end in the pseudo-class instead, so they can never satisfy the resting
    suffix, and vice versa."""
    values = []
    for _order, selector, body in _iter_rules(css):
        if selector.strip().endswith(suffix):
            for value, _important in _declarations(body, (prop,)):
                values.append(value.strip())
    return values


@tagged("post_install", "-at_install")
class TestPivotDarkCompile(TransactionCase):
    """Pivot text and its header hover band read correctly once compiled through
    web.assets_backend_lazy_dark; the sibling light lazy bundle is untouched."""

    def _compiled_css(self, bundle_name):
        """Compile ``bundle_name`` and return its CSS payload as decoded text (19.0 API:
        ``ir.qweb._get_asset_bundle(name, css=True, js=False).css()`` - same contract every
        sibling compile test in this module already uses)."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so the pivot dark palette "
            "cannot be verified." % bundle_name,
        )
        return css

    def _single_value(self, css, bundle_name, suffix, prop, state_label):
        values = [
            colour for colour in (
                _normalize_colour(value) for value in _values_ending_with(css, suffix, prop)
            ) if colour
        ]
        self.assertTrue(
            values,
            "no %s declared on a rule ending in %r in %s - %s is missing from this bundle."
            % (prop, suffix, bundle_name, state_label),
        )
        # Equal-scope declarations: the last in source order is the effective one, matching every
        # sibling compile test's own cascade convention in this module.
        return values[-1]

    def _light_link_color_ssot(self):
        """Return the hex ``$o-main-link-color`` resolves to in brand_variables.scss - the exact
        variable core's ``pivot_view.scss`` feeds into ``o-hover-text-color($body-color,
        $o-main-link-color)`` for the enable_linking value-cell hover/focus state (confirmed by
        reading that core file directly). Read live so a future re-tune of this module's own link
        colour cannot silently desync from what this test expects."""
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            value = _resolve_scss_hex(scss_file.read(), "$o-main-link-color")
        self.assertIsNotNone(
            value,
            "$o-main-link-color must be declared in %s - the pivot value-cell hover/focus guard "
            "reads its expected light colour from this SSOT rather than re-literalising it."
            % os.path.basename(BRAND_VARIABLES_SCSS),
        )
        return value.lower()

    def _light_bootstrap_default(self, backend_css, prop):
        """Return the hex Bootstrap's own default chain resolves ``--<prop>`` to on :root in a
        compiled web.assets_backend css. Odoo compiles Bootstrap with `$variable-prefix: ''`
        (web/static/src/scss/bootstrap_overridden.scss), so the custom property is UNPREFIXED -
        confirmed live off this same bundle's own :root rule rather than assumed. web.assets_backend
        is the always-loaded bundle that carries Bootstrap's own `_root.scss` custom-property block,
        unlike the two pivot lazy bundles this file compiles elsewhere - so it is this cluster's
        live source for a Bootstrap default core's pivot_view.scss consumes but this module does not
        declare anywhere in its own scss (there is no in-repo SSOT for $body-color /
        map-get($grays, "200") / $headings-color to read instead)."""
        custom_prop = "--" + prop
        values = [
            colour for colour in (
                _normalize_colour(value)
                for _order, selector, body in _iter_rules(backend_css)
                if selector == ":root"
                for value, _important in _declarations(body, (custom_prop,))
            ) if colour
        ]
        self.assertTrue(
            values,
            "no %s declared on :root in %s - Bootstrap's own default for this token could not be "
            "read live." % (custom_prop, BACKEND_BUNDLE),
        )
        return values[-1]

    # ------------------------------------------------------------------------------------------
    # DARK: pivot header / measure-row / value-cell text is readable against the dark panel
    # ------------------------------------------------------------------------------------------
    def test_pivot_header_and_value_text_reads_the_dark_body_colour(self):
        """Every resting (non-hover) pivot text surface must compile to #EDF4F5 in the dark lazy
        bundle - 15.55:1 on the #111B1E panel. RED before the fix: today this bundle is a bare
        include of the light one, so it still compiles the light #212529 (~1.1:1 on #111B1E)."""
        css = self._compiled_css(PIVOT_LAZY_DARK_BUNDLE)
        ratio = _contrast_ratio(DARK_READABLE_TEXT, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "sanity: the design's own DARK_READABLE_TEXT/DARK_BODY_BG pair measures only %.2f:1."
            % ratio,
        )
        for selector in _HEADER_SELECTORS:
            colour = self._single_value(
                css, PIVOT_LAZY_DARK_BUNDLE, selector, "color", "the resting header/measure text",
            )
            self.assertEqual(
                colour, DARK_READABLE_TEXT,
                "%s must compile to the dark body text %s in %s; got %s (the unchanged light "
                "value means dark_palette.scss never reached this bundle)."
                % (selector, DARK_READABLE_TEXT, PIVOT_LAZY_DARK_BUNDLE, colour),
            )
        value_colour = self._single_value(
            css, PIVOT_LAZY_DARK_BUNDLE, _VALUE_CELL_SELECTOR, "color", "the resting value-cell text",
        )
        self.assertEqual(
            value_colour, DARK_READABLE_TEXT,
            "%s must compile to the dark body text %s in %s; got %s."
            % (_VALUE_CELL_SELECTOR, DARK_READABLE_TEXT, PIVOT_LAZY_DARK_BUNDLE, value_colour),
        )

    # ------------------------------------------------------------------------------------------
    # DARK: the header hover band is a subtle tint, and its label stays readable on it
    # ------------------------------------------------------------------------------------------
    def test_pivot_header_hover_band_is_a_subtle_tint_with_a_readable_label(self):
        """The header hover background must sit close to the resting dark panel (<= 2:1) - a
        tint, not the light bundle's hard swap to #E9ECEF (a >= 9:1 jump off #111B1E) - while the
        hover label itself stays >= 4.5:1 against whatever that band resolves to.

        RED before the fix: the dark bundle still compiles the light hover band #E9ECEF, which
        measures far more than 2:1 off the dark panel."""
        css = self._compiled_css(PIVOT_LAZY_DARK_BUNDLE)
        for selector in _HEADER_SELECTORS:
            hover_suffix = selector + ":hover"
            band = self._single_value(
                css, PIVOT_LAZY_DARK_BUNDLE, hover_suffix, "background-color",
                "the header hover band",
            )
            band_ratio = _contrast_ratio(DARK_BODY_BG, band)
            self.assertLessEqual(
                round(band_ratio, 2), HOVER_BAND_MAX_CONTRAST,
                "%s hover background %s measures %.2f:1 off the dark panel %s - above the %.1f:1 "
                "subtle-tint bound, so hovering a header cell still reads as a hard flash rather "
                "than a tint." % (selector, band, band_ratio, DARK_BODY_BG, HOVER_BAND_MAX_CONTRAST),
            )
            label = self._single_value(
                css, PIVOT_LAZY_DARK_BUNDLE, hover_suffix, "color", "the header hover label",
            )
            label_ratio = _contrast_ratio(label, band)
            self.assertGreaterEqual(
                round(label_ratio, 2), WCAG_AA_NORMAL_TEXT,
                "%s hover label %s measures only %.2f:1 on its own hover band %s, below WCAG AA "
                "%.1f:1." % (selector, label, label_ratio, band, WCAG_AA_NORMAL_TEXT),
            )

    # ------------------------------------------------------------------------------------------
    # DARK: the COMPILED header hover band must equal $body-tertiary-bg's own resolved value
    # ------------------------------------------------------------------------------------------
    def test_header_hover_band_compiles_to_the_dark_palette_raised_rung_variable(self):
        """The dark bundle's compiled header hover-background must equal dark_palette.scss's own
        ``$body-tertiary-bg``, read live from that file - not merely satisfy the sibling test's
        ratio-only subtle-tint bound above. Companion assertion: this fails the moment the
        compiled value drifts from the named SSOT variable, even while still inside that bound."""
        css = self._compiled_css(PIVOT_LAZY_DARK_BUNDLE)
        expected = dark_palette_var("$body-tertiary-bg")
        for selector in _HEADER_SELECTORS:
            hover_suffix = selector + ":hover"
            band = self._single_value(
                css, PIVOT_LAZY_DARK_BUNDLE, hover_suffix, "background-color",
                "the header hover band",
            )
            self.assertEqual(
                _normalize_colour(band), expected,
                "%s hover background %s does not match dark_palette.scss's own "
                "$body-tertiary-bg %s - the hover band has drifted from its raised-rung SSOT."
                % (hover_suffix, band, expected),
            )

    # ------------------------------------------------------------------------------------------
    # LIGHT: untouched
    # ------------------------------------------------------------------------------------------
    def test_light_lazy_bundle_pivot_colours_stay_unchanged(self):
        """web.assets_backend_lazy (light) must keep compiling pivot text/hover colours that equal
        Bootstrap's own --body-color / --heading-color / --gray-200 defaults (unprefixed - Odoo
        sets $variable-prefix: ''), read live off web.assets_backend's :root - this bundle carries
        the ONLY light-mode arm of pivot_view.scss's tokens, so a change meant for the dark bundle
        must not also move it."""
        css = self._compiled_css(PIVOT_LAZY_LIGHT_BUNDLE)
        backend_css = self._compiled_css(BACKEND_BUNDLE)
        light_body_color = self._light_bootstrap_default(backend_css, "body-color")
        light_heading_color = self._light_bootstrap_default(backend_css, "heading-color")
        light_gray_200 = self._light_bootstrap_default(backend_css, "gray-200")
        for selector in _HEADER_SELECTORS:
            resting = self._single_value(
                css, PIVOT_LAZY_LIGHT_BUNDLE, selector, "color", "the resting header/measure text",
            )
            self.assertEqual(
                resting, light_body_color,
                "%s must keep compiling to Bootstrap's own --body-color (%s) in %s; got %s."
                % (selector, light_body_color, PIVOT_LAZY_LIGHT_BUNDLE, resting),
            )
            hover_suffix = selector + ":hover"
            hover_text = self._single_value(
                css, PIVOT_LAZY_LIGHT_BUNDLE, hover_suffix, "color", "the header hover label",
            )
            self.assertEqual(
                hover_text, light_heading_color,
                "%s hover label must stay Bootstrap's own --heading-color (%s) in %s; got %s."
                % (selector, light_heading_color, PIVOT_LAZY_LIGHT_BUNDLE, hover_text),
            )
            hover_bg = self._single_value(
                css, PIVOT_LAZY_LIGHT_BUNDLE, hover_suffix, "background-color", "the header hover band",
            )
            self.assertEqual(
                hover_bg, light_gray_200,
                "%s hover band must stay Bootstrap's own --gray-200 (%s) in %s; got %s."
                % (selector, light_gray_200, PIVOT_LAZY_LIGHT_BUNDLE, hover_bg),
            )
        value_resting = self._single_value(
            css, PIVOT_LAZY_LIGHT_BUNDLE, _VALUE_CELL_SELECTOR, "color", "the resting value-cell text",
        )
        self.assertEqual(
            value_resting, light_body_color,
            "%s must keep compiling to Bootstrap's own --body-color (%s) in %s; got %s."
            % (_VALUE_CELL_SELECTOR, light_body_color, PIVOT_LAZY_LIGHT_BUNDLE, value_resting),
        )
        value_hover = self._single_value(
            css, PIVOT_LAZY_LIGHT_BUNDLE, _VALUE_CELL_SELECTOR + ":hover", "color",
            "the value-cell hover/link colour",
        )
        expected_value_hover = self._light_link_color_ssot()
        self.assertEqual(
            value_hover, expected_value_hover,
            "%s hover must keep compiling to $o-main-link-color's own value (%s) in %s; got %s."
            % (_VALUE_CELL_SELECTOR, expected_value_hover, PIVOT_LAZY_LIGHT_BUNDLE, value_hover),
        )
