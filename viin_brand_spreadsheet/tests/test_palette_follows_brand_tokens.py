# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import os
import re

from odoo.modules import get_module_path
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

TOKENS_CSS = os.path.join("static", "src", "css", "spreadsheet_tokens.css")
DARK_PALETTE_SCSS = os.path.join(os.path.dirname(BRAND_VARIABLES_SCSS), "dark_palette.scss")
PAIR = r"--%s\s*:\s*light-dark\(\s*(#[0-9a-fA-F]{6})\s*,\s*(#[0-9a-fA-F]{6})\s*\)"
MIX = r"^\s*%s\s*:\s*mix\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(\d+)%%\s*\)\s*;"
KEYWORDS = {"white": "#ffffff", "black": "#000000"}


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _channels(colour):
    return [int(colour[i:i + 2], 16) for i in (1, 3, 5)]


def _sass_mix(first, second, weight):
    """Sass's mix() of two opaque colours: ``weight`` percent of ``first``."""
    ratio = weight / 100.0
    mixed = [round(a * ratio + b * (1 - ratio)) for a, b in zip(_channels(first), _channels(second))]
    return "#%02x%02x%02x" % tuple(mixed)


def _resolve(scss, name):
    """The hex a Sass token resolves to: a literal, an alias or a mix() of two such colours."""
    if name in KEYWORDS:
        return KEYWORDS[name]
    if name.startswith("#"):
        return name.lower()
    hex_value = _resolve_scss_hex(scss, name)
    if hex_value:
        return hex_value.lower()
    match = re.search(MIX % re.escape(name), scss, re.MULTILINE)
    if not match:
        return None
    first, second = _resolve(scss, match.group(1)), _resolve(scss, match.group(2))
    if not (first and second):
        return None
    return _sass_mix(first, second, int(match.group(3)))


@tagged("post_install", "-at_install")
class TestSpreadsheetPaletteFollowsTheBrandTokens(TransactionCase):
    """The editor repeats the brand colours as literals, because a custom property cannot read a Sass
    token; the literals must stay equal to the content tokens of viin_brand, one arm per scheme. The
    dark scheme reads dark_palette.scss first, then the shared declarations of brand_variables.scss,
    as the dark bundle compiles them."""

    def _arms(self, token):
        css = _read(os.path.join(get_module_path("viin_brand_spreadsheet"), TOKENS_CSS))
        match = re.search(PAIR % re.escape(token), css)
        self.assertTrue(match, "the editor palette declares no %s" % token)
        return match.group(1).lower(), match.group(2).lower()

    def _token(self, name, dark=False):
        scss = _read(BRAND_VARIABLES_SCSS)
        if dark:
            scss = _read(DARK_PALETTE_SCSS) + "\n" + scss
        value = _resolve(scss, name)
        self.assertTrue(value, "viin_brand declares no %s" % name)
        return value

    def _primary_button_state(self, key):
        """A state colour of the "primary" entry of the button map, which spells them as literals."""
        match = re.search(r"%s:\s*(#[0-9A-Fa-f]{6})" % re.escape(key), _read(BRAND_VARIABLES_SCSS))
        self.assertTrue(match, "the primary button map declares no %s" % key)
        return match.group(1).lower()

    def test_primary_button_fill_is_the_content_colour_of_each_scheme(self):
        self.assertEqual(
            self._arms("os-primary-button-bg"),
            (self._token("$o-brand-primary"), self._token("$o-brand-primary", dark=True)),
        )

    def test_primary_button_hover_follows_the_action_ladder(self):
        self.assertEqual(
            self._arms("os-primary-button-hover-bg"),
            (self._primary_button_state("hover-background"), self._token("$o-viin-dark-action-hover", dark=True)),
        )

    def test_primary_button_label_is_the_action_label_of_each_scheme(self):
        self.assertEqual(
            self._arms("os-primary-button-text-color"),
            (self._token("$o-viin-action-label"), self._token("$o-viin-action-label", dark=True)),
        )

    def test_pressed_button_is_the_tint_under_the_button_colour(self):
        self.assertEqual(
            self._arms("os-primary-button-active-bg"),
            (self._primary_button_state("active-background"), self._token("$o-component-active-bg", dark=True)),
        )

    def test_links_follow_the_content_link_tokens(self):
        self.assertEqual(
            self._arms("os-link-color"),
            (self._token("$o-main-link-color"), self._token("$o-main-link-color", dark=True)),
        )
        self.assertEqual(
            self._arms("os-link-hover-color"),
            (self._token("$o-viin-action-deep"), self._token("$link-hover-color", dark=True)),
        )

    def test_content_arms_are_not_the_chrome_tokens(self):
        chrome = {self._token("$o-viin-chrome-base"), self._token("$o-viin-chrome-deep")}
        for token in (
            "os-link-color", "os-link-hover-color", "os-primary-button-bg",
            "os-primary-button-hover-bg", "os-primary-button-active-bg",
        ):
            with self.subTest(token=token):
                self.assertFalse(chrome & set(self._arms(token)))

    def test_selected_button_fill_is_the_tint_and_the_control_rung(self):
        self.assertEqual(
            self._arms("os-button-active-bg"),
            (self._primary_button_state("active-background"), self._token("$o-viin-dark-control-bg", dark=True)),
        )
