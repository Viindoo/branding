# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Once `viin_brand` contributes its dark palette to `web.assets_backend_lazy_dark` (the bundle
# `web/static/src/views/view.js` loads whenever `cookie.get("color_scheme") === "dark"` before
# mounting a pivot or graph view; `web/__manifest__.py` declares it as a bare
# `('include', 'web.assets_backend_lazy')`, carrying none of the brand's dark tokens), the pivot's
# own text must be readable against the dark panel, its header's hover state must read as a subtle
# tint on rung 200 of the dark gray ramp with a readable label, and the sibling light lazy bundle
# must compile unchanged.
#
# The compiled CSS is read because `web/static/src/views/pivot/pivot_view.scss` declares every
# colour under test via one Sass variable each - `$body-color` for the resting header/measure/value
# text (`@include o-hover-text-color($body-color, $headings-color)` and the enable_linking
# value-cell rule), `map-get($grays, "200")` for the hover band and `$headings-color` for the hover
# label. `web.assets_backend_lazy` compiles only variable-declaration partials plus `graph/**` and
# `pivot/**` (no `web/static/lib/bootstrap/scss/_root.scss`), so none of these reach the page as a
# `var()` custom property: each bakes in as a literal hex when the bundle compiles.
#
# Dark values (literals):
#   resting text      #EDF4F5 on the panel #111B1E (DARK_READABLE_TEXT / DARK_BODY_BG)
#   hover band        #1D2D31 - rung 200 of the dark gray ramp, 1.23:1 off the panel
#   hover label       #C9D6D8 on the band, 9.57:1
#
# Light values (the unchanged baseline of `web.assets_backend_lazy`):
#   .o_pivot_measure_row / .o_pivot_origin_row / .o_pivot_header_cell_closed /
#   .o_pivot_header_cell_opened      resting color: #212529     hover color: #000000
#                                     hover background-color: #e9ecef !important
#   .o_pivot_cell_value:not(.o_empty) (enable_linking)  resting color: #212529
#                                                        hover/focus color: $o-main-link-color's
#                                                        own value, read from brand_variables.scss
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
)
from .test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

PIVOT_LAZY_DARK_BUNDLE = "web.assets_backend_lazy_dark"
PIVOT_LAZY_LIGHT_BUNDLE = "web.assets_backend_lazy"

# Header / measure-row selectors that share one compiled rule per state in core's pivot_view.scss.
# Checked individually so a split of that rule cannot drop one of the four from coverage.
_HEADER_SELECTORS = (
    ".o_pivot_measure_row",
    ".o_pivot_origin_row",
    ".o_pivot_header_cell_closed",
    ".o_pivot_header_cell_opened",
)
_VALUE_CELL_SELECTOR = ".o_pivot_cell_value:not(.o_empty)"

# "A subtle tint, not a hard swap": an upper bound on how far the hover background may sit from the
# resting one. It is a proximity bound, not a WCAG threshold (those are minimums).
HOVER_BAND_MAX_CONTRAST = 2.0

# Rung 200 of the dark gray ramp (dark_palette.scss `$o-gray-200`) - the band core's pivot_view.scss
# paints on a hovered header through `map-get($grays, "200")` - and the dark emphasis text core
# keeps for the hover label (`$headings-color`).
DARK_PIVOT_HOVER_BAND = "#1d2d31"
DARK_PIVOT_HOVER_LABEL = "#c9d6d8"


def _values_ending_with(css, suffix, prop):
    """Every ``prop`` value declared on a rule whose selector ends EXACTLY in ``suffix``.

    ``_iter_rules`` yields one full compound selector per call, so a plain ``str.endswith``
    tells the resting compound (``...o_pivot_header_cell_closed``) apart from its
    ``:hover``/``:focus`` siblings, which end in the pseudo-class."""
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
        """Compile ``bundle_name`` and return its CSS payload as decoded text."""
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
        # Equal-scope declarations: the last in source order is the effective one.
        return values[-1]

    def _light_link_color_ssot(self):
        """Return the hex ``$o-main-link-color`` resolves to in brand_variables.scss - the variable
        core's ``pivot_view.scss`` feeds into ``o-hover-text-color($body-color,
        $o-main-link-color)`` for the enable_linking value-cell hover/focus state."""
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
        (web/static/src/scss/bootstrap_overridden.scss), so the custom property is unprefixed.
        web.assets_backend carries Bootstrap's `_root.scss` block, unlike the pivot lazy bundles, so
        it is the source for a Bootstrap default that core's pivot_view.scss consumes and this
        module does not declare ($body-color, map-get($grays, "200"), $headings-color)."""
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

    def test_pivot_header_and_value_text_reads_the_dark_body_colour(self):
        """Every resting (non-hover) pivot text surface must compile to #EDF4F5 in the dark lazy
        bundle - 15.55:1 on the #111B1E panel; the light #212529 would be ~1.1:1 on it."""
        css = self._compiled_css(PIVOT_LAZY_DARK_BUNDLE)
        ratio = _contrast_ratio(DARK_READABLE_TEXT, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "sanity: the DARK_READABLE_TEXT/DARK_BODY_BG pair measures only %.2f:1."
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

    def test_pivot_header_hover_band_is_a_subtle_tint_with_a_readable_label(self):
        """The header hover background must sit close to the resting dark panel (<= 2:1) - a
        tint, not the light bundle's hard swap to #E9ECEF (a >= 9:1 jump off #111B1E) - while the
        hover label itself stays >= 4.5:1 against whatever that band resolves to."""
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

    def test_header_hover_band_is_ramp_rung_200_with_the_emphasis_label(self):
        """The dark bundle's header hover background is #1D2D31 and the hover label #C9D6D8, which
        read 9.57:1 on that band. Asserts literal values, so it fails the moment either
        drifts, even while still inside the sibling test's looser tint and AA bounds."""
        css = self._compiled_css(PIVOT_LAZY_DARK_BUNDLE)
        self.assertGreaterEqual(
            round(_contrast_ratio(DARK_PIVOT_HOVER_LABEL, DARK_PIVOT_HOVER_BAND), 1), 9.5,
            "sanity: the hover label/band pair must measure about 9.6:1.",
        )
        for selector in _HEADER_SELECTORS:
            hover_suffix = selector + ":hover"
            band = self._single_value(
                css, PIVOT_LAZY_DARK_BUNDLE, hover_suffix, "background-color",
                "the header hover band",
            )
            self.assertEqual(
                _normalize_colour(band), DARK_PIVOT_HOVER_BAND,
                "%s hover background %s is not the dark gray ramp's rung 200 %s."
                % (hover_suffix, band, DARK_PIVOT_HOVER_BAND),
            )
            label = self._single_value(
                css, PIVOT_LAZY_DARK_BUNDLE, hover_suffix, "color", "the header hover label",
            )
            self.assertEqual(
                _normalize_colour(label), DARK_PIVOT_HOVER_LABEL,
                "%s hover label %s is not the dark emphasis text %s."
                % (hover_suffix, label, DARK_PIVOT_HOVER_LABEL),
            )

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
