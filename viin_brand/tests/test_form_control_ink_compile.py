# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Three Bootstrap form/close controls bake their ink colour into a Sass value at compile time
# rather than deriving it from a token the dark recompile moves - `$btn-close-color`
# (bootstrap/scss/_variables.scss), `$form-switch-color` and `$form-select-indicator-color`. Two of
# the three bake that colour inside a `data:image/svg+xml` data-URI (`escape-svg()` percent-encodes
# it), so the SVG markup has to be decoded first. Every assertion measures the resolved WCAG
# contrast ratio of the compiled ink against the dark surface it sits on (SC 1.4.11 non-text,
# floor 3:1), never a hex-equality snapshot.
#
# As in test_focus_ring_compile.py, the property is read out of the compiled
# `web.assets_web_dark` bundle rather than grepped from a .scss file.
import re

from odoo.tests.common import TransactionCase, tagged

# _winning_declaration resolves a property's cascade-winning value for a modelled element, needed
# wherever a state variant (:focus) redeclares the same custom property as its resting state.
from .test_brand_cascade_compile import (
    DARK_BODY_BG,
    DARK_BUNDLE,
    WCAG_NON_TEXT_MIN,
    _alpha_of,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    _winning_declaration,
)

# The plain (non-baked) custom property .btn-close emits its ink through (_close.scss) - a direct
# scalar read, no SVG decoding needed. Odoo compiles Bootstrap with an empty `$prefix`
# (bootstrap_overridden.scss), so the compiled custom property carries no `bs-` prefix.
BTN_CLOSE_COLOR_PROP = "btn-close-color"
BTN_CLOSE_OPACITY_PROP = "btn-close-opacity"
# .accordion-button declares this once, unconditionally, in its own base rule
# (bootstrap/scss/_accordion.scss) - it is not redeclared per state, only CONSUMED conditionally
# by the `:not(.collapsed)` rule, so a plain last-match read is unambiguous here too.
ACCORDION_ACTIVE_ICON_PROP = "accordion-btn-active-icon"

# `--form-switch-bg` is redeclared three times on the same element - resting, :focus and :checked
# (bootstrap/scss/forms/_form-check.scss) - so the state-correct rule is picked by the cascade
# engine (`_winning_declaration`) on a modelled element rather than by a last-match read.
FORM_SWITCH_BG_DECL = "--form-switch-bg"

# .form-select's own base rule (forms/_form-select.scss) is the only Bootstrap-authored declaration
# of this property, but mail's "simulate dark theme" preview utility also redeclares it, scoped to
# `.o-discuss-dropdownMenu.o-simulateDarkTheme .form-select`, and compiles later in the bundle. A
# last-match read would return that unrelated value; modelling a real element with no ancestor
# context lets the cascade engine's ancestor-scope check exclude it.
FORM_SELECT_BG_IMG_DECL = "--form-select-bg-img"
FORM_SELECT_ELEMENT = {"classes": frozenset({"form-select"}), "ancestors": frozenset()}
FORM_SWITCH_INPUT = {
    "classes": frozenset({"form-check-input"}),
    "ancestors": frozenset({"form-switch"}),
}
FORM_SWITCH_INPUT_FOCUSED = dict(FORM_SWITCH_INPUT, states=frozenset({"focus"}))

# The valid/invalid feedback icon is not a custom property: Bootstrap bakes it into a
# `background-image:` declaration on `.form-control.is-valid` / `.is-invalid`
# (bootstrap/scss/mixins/_forms.scss).
FORM_CONTROL_VALID = {"classes": frozenset({"form-control", "is-valid"}), "ancestors": frozenset()}
FORM_CONTROL_INVALID = {"classes": frozenset({"form-control", "is-invalid"}), "ancestors": frozenset()}

# Bootstrap's escape-svg() (bootstrap/scss/_functions.scss) percent-encodes exactly the five
# characters in $escaped-characters (bootstrap/scss/_variables.scss) before baking SVG markup into
# a custom property; reversing that map lets _normalize_colour/_alpha_of read the colour back.
_SVG_UNESCAPE_MAP = {"%3c": "<", "%3e": ">", "%23": "#", "%28": "(", "%29": ")"}
_SVG_UNESCAPE_RE = re.compile("|".join(re.escape(k) for k in _SVG_UNESCAPE_MAP), re.IGNORECASE)


def _unescape_svg(value):
    return _SVG_UNESCAPE_RE.sub(lambda m: _SVG_UNESCAPE_MAP[m.group(0).lower()], value)


def _custom_prop_value(css, prop_name):
    """Return the last declared value of a bare ``--<prop_name>`` custom property in css, or None."""
    matches = re.findall(r"--%s\s*:\s*([^;}]+)" % re.escape(prop_name), css)
    return matches[-1].strip() if matches else None


def _baked_svg_attr_colour(raw_value, attr_name):
    """Return ``(hex, alpha)`` for ``attr_name='<colour>'`` inside a baked SVG data-URI declaration,
    or ``(None, None)`` when either the declaration or the attribute is absent. ``raw_value`` is
    the declaration text exactly as the cascade resolved it - still escape-svg()-encoded."""
    if raw_value is None:
        return None, None
    decoded = _unescape_svg(raw_value)
    match = re.search(r"%s=(['\"])(.*?)\1" % re.escape(attr_name), decoded)
    if match is None:
        return None, None
    spelling = match.group(2)
    return _normalize_colour(spelling), _alpha_of(spelling)


def _rendered_against(hex_colour, alpha, surface):
    """The pixel a viewer actually reads: ``hex_colour`` alpha-composited over ``surface`` when the
    baked colour itself carries translucency (e.g. the stock ``rgba($black, .25)`` switch fill)."""
    return hex_colour if alpha >= 1.0 else _composite_over(hex_colour, surface, alpha)


@tagged("post_install", "-at_install")
class FormControlInkCompileTest(TransactionCase):

    def _compiled_css(self, bundle_name):
        """Compile an asset bundle by name and return its CSS payload as decoded text."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so no ink token can be "
            "verified." % bundle_name,
        )
        return css

    def test_btn_close_ink_clears_non_text_contrast_on_the_dark_panel(self):
        css = self._compiled_css(DARK_BUNDLE)
        colour = _normalize_colour(_custom_prop_value(css, BTN_CLOSE_COLOR_PROP))
        self.assertIsNotNone(
            colour,
            "No --%s resolves to a colour in %s - .btn-close (_close.scss) is missing from this "
            "bundle." % (BTN_CLOSE_COLOR_PROP, DARK_BUNDLE),
        )
        opacity_raw = _custom_prop_value(css, BTN_CLOSE_OPACITY_PROP)
        opacity = float(opacity_raw) if opacity_raw else 1.0
        rendered = _rendered_against(colour, opacity, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The modal/dialog close icon --%s=%s at opacity %s composites to %s on the dark panel "
            "%s = %.2f:1, below the WCAG SC 1.4.11 non-text floor of %.1f:1 - the close control is "
            "not reliably visible in dark mode." % (
                BTN_CLOSE_COLOR_PROP, colour, opacity, rendered, DARK_BODY_BG, ratio,
                WCAG_NON_TEXT_MIN,
            ),
        )

    def test_form_switch_unchecked_knob_ink_clears_non_text_contrast_on_the_dark_track(self):
        css = self._compiled_css(DARK_BUNDLE)
        raw = _winning_declaration(css, FORM_SWITCH_INPUT, (FORM_SWITCH_BG_DECL,))
        self.assertIsNotNone(
            raw,
            "No %s resolves on .form-switch .form-check-input in %s - "
            "forms/_form-check.scss is missing from this bundle." % (
                FORM_SWITCH_BG_DECL, DARK_BUNDLE,
            ),
        )
        colour, alpha = _baked_svg_attr_colour(raw, "fill")
        self.assertIsNotNone(
            colour,
            "The resting %s SVG in %s carries no readable fill colour: %r" % (
                FORM_SWITCH_BG_DECL, DARK_BUNDLE, raw,
            ),
        )
        rendered = _rendered_against(colour, alpha, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The unchecked form-switch knob fill=%s (alpha %s, renders as %s) clears only %.2f:1 "
            "against its dark track %s, below the WCAG SC 1.4.11 non-text floor of %.1f:1 - an "
            "unchecked toggle is invisible in dark mode." % (
                colour, alpha, rendered, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN,
            ),
        )

    def test_form_select_caret_ink_clears_non_text_contrast_on_the_dark_input(self):
        css = self._compiled_css(DARK_BUNDLE)
        raw = _winning_declaration(css, FORM_SELECT_ELEMENT, (FORM_SELECT_BG_IMG_DECL,))
        self.assertIsNotNone(
            raw,
            "No %s resolves on .form-select in %s - forms/_form-select.scss is missing from "
            "this bundle." % (FORM_SELECT_BG_IMG_DECL, DARK_BUNDLE),
        )
        colour, alpha = _baked_svg_attr_colour(raw, "stroke")
        self.assertIsNotNone(
            colour,
            "The %s SVG in %s carries no readable stroke colour: %r" % (
                FORM_SELECT_BG_IMG_DECL, DARK_BUNDLE, raw,
            ),
        )
        rendered = _rendered_against(colour, alpha, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The <select> caret stroke=%s (renders as %s) clears only %.2f:1 against its dark "
            "input surface %s, below the WCAG SC 1.4.11 non-text floor of %.1f:1 - the dropdown "
            "affordance is not reliably visible in dark mode." % (
                colour, rendered, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN,
            ),
        )

    def test_form_switch_focus_state_image_clears_non_text_contrast_on_the_dark_track(self):
        css = self._compiled_css(DARK_BUNDLE)
        raw = _winning_declaration(
            css, FORM_SWITCH_INPUT_FOCUSED, (FORM_SWITCH_BG_DECL,)
        )
        self.assertIsNotNone(
            raw,
            "No %s resolves on .form-switch .form-check-input:focus in %s." % (
                FORM_SWITCH_BG_DECL, DARK_BUNDLE,
            ),
        )
        colour, alpha = _baked_svg_attr_colour(raw, "fill")
        self.assertIsNotNone(
            colour,
            "The :focus %s SVG in %s carries no readable fill colour: %r" % (
                FORM_SWITCH_BG_DECL, DARK_BUNDLE, raw,
            ),
        )
        rendered = _rendered_against(colour, alpha, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The focused form-switch knob fill=%s (renders as %s) clears only %.2f:1 against its "
            "dark track %s, below the WCAG SC 1.4.11 non-text floor of %.1f:1." % (
                colour, rendered, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN,
            ),
        )

    def test_accordion_active_icon_clears_non_text_contrast_on_the_dark_panel(self):
        css = self._compiled_css(DARK_BUNDLE)
        raw = _custom_prop_value(css, ACCORDION_ACTIVE_ICON_PROP)
        self.assertIsNotNone(
            raw,
            "No --%s resolves to a value in %s - .accordion-button is missing from this bundle." % (
                ACCORDION_ACTIVE_ICON_PROP, DARK_BUNDLE,
            ),
        )
        colour, alpha = _baked_svg_attr_colour(raw, "stroke")
        self.assertIsNotNone(
            colour,
            "The --%s SVG in %s carries no readable stroke colour: %r" % (
                ACCORDION_ACTIVE_ICON_PROP, DARK_BUNDLE, raw,
            ),
        )
        rendered = _rendered_against(colour, alpha, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The open-accordion chevron stroke=%s (renders as %s) clears only %.2f:1 against the "
            "dark panel %s, below the WCAG SC 1.4.11 non-text floor of %.1f:1." % (
                colour, rendered, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN,
            ),
        )

    def test_valid_feedback_icon_clears_non_text_contrast_on_the_dark_input(self):
        css = self._compiled_css(DARK_BUNDLE)
        raw = _winning_declaration(css, FORM_CONTROL_VALID, ("background-image",))
        self.assertIsNotNone(
            raw,
            "No background-image resolves on .form-control.is-valid in %s." % DARK_BUNDLE,
        )
        colour, alpha = _baked_svg_attr_colour(raw, "fill")
        self.assertIsNotNone(
            colour,
            "The .form-control.is-valid background-image SVG in %s carries no readable fill "
            "colour: %r" % (DARK_BUNDLE, raw),
        )
        rendered = _rendered_against(colour, alpha, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The valid-feedback checkmark fill=%s (renders as %s) clears only %.2f:1 against the "
            "dark input surface %s, below the WCAG SC 1.4.11 non-text floor of %.1f:1." % (
                colour, rendered, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN,
            ),
        )

    def test_invalid_feedback_icon_clears_non_text_contrast_on_the_dark_input(self):
        css = self._compiled_css(DARK_BUNDLE)
        raw = _winning_declaration(css, FORM_CONTROL_INVALID, ("background-image",))
        self.assertIsNotNone(
            raw,
            "No background-image resolves on .form-control.is-invalid in %s." % DARK_BUNDLE,
        )
        colour, alpha = _baked_svg_attr_colour(raw, "stroke")
        self.assertIsNotNone(
            colour,
            "The .form-control.is-invalid background-image SVG in %s carries no readable stroke "
            "colour: %r" % (DARK_BUNDLE, raw),
        )
        rendered = _rendered_against(colour, alpha, DARK_BODY_BG)
        ratio = _contrast_ratio(rendered, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The invalid-feedback icon stroke=%s (renders as %s) clears only %.2f:1 against the "
            "dark input surface %s, below the WCAG SC 1.4.11 non-text floor of %.1f:1." % (
                colour, rendered, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN,
            ),
        )
