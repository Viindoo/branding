# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The spreadsheet editor paints every colour of its chrome from the --os-* custom properties, so the
# palette is read from a real editor: each token through a probe element inside the editor root, and
# the chrome through the surfaces the user looks at.
import json

from odoo.tests import HttpCase, new_test_user, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _normalize_colour,
)
from odoo.addons.viin_brand.tests.test_scheme_cookie_first_load import _wrap

EDITOR_URL = "/odoo/action-viin_brand_spreadsheet_palette_test_editor"

TOKEN_EXPECTATIONS = {
    "light": {
        "--os-primary-button-bg": "#7f4282",
        "--os-primary-button-hover-bg": "#663568",
        "--os-primary-button-active-bg": "#f2ecf2",
        "--os-link-color": "#7f4282",
        "--os-link-hover-color": "#592e5b",
        "--os-button-active-bg": "#f2ecf2",
        "--os-primary-button-text-color": "#ffffff",
    },
    "dark": {
        "--os-primary-button-bg": "#00bbce",
        "--os-primary-button-hover-bg": "#26c5d5",
        "--os-primary-button-active-bg": "#114147",
        "--os-primary-button-text-color": "#21272b",
        "--os-link-color": "#00bbce",
        "--os-link-hover-color": "#66d6e2",
        "--os-button-active-bg": "#25383c",
        "--os-gray-100": "#152225",
        "--os-gray-300": "#25383c",
        "--os-white-bg": "#111b1e",
        "--os-active-sheet-bg": "#25383c",
    },
}
LIGHT_ODOO_PURPLE_AND_TEAL = ("#714b67", "#017e84")

_MEASURE_JS = """
const __root = await __waitFor(() => document.querySelector('.o-spreadsheet'), 60000);
const __tokens = %(tokens)s;
const __resolved = {};
for (const token of __tokens) {
    const probe = document.createElement('div');
    probe.style.backgroundColor = 'var(' + token + ')';
    __root.appendChild(probe);
    __resolved[token] = getComputedStyle(probe).backgroundColor;
    probe.remove();
}
const __surface = (selector) => {
    const el = document.querySelector(selector);
    if (!el) { return null; }
    return {
        background: __effectiveBackground(el),
        color: getComputedStyle(el).color,
    };
};
await __setParam(%(key)r, JSON.stringify({
    tokens: __resolved,
    topbar: __surface('.o-spreadsheet-topbar-wrapper'),
    bottombar: __surface('.o-spreadsheet-bottombar-wrapper'),
    activeSheet: __surface('.o-sheet.active'),
}));
"""


@tagged("post_install", "-at_install")
class TestSpreadsheetPalette(HttpCase):

    def _measure(self, scheme):
        user = new_test_user(
            self.env, login="viin_sheet_palette_%s" % scheme,
            groups="base.group_user,base.group_system", viin_color_scheme=scheme,
        )
        key = "viin_brand_spreadsheet.palette_test.%s" % scheme
        tokens = sorted(set(TOKEN_EXPECTATIONS["light"]) | set(TOKEN_EXPECTATIONS["dark"]))
        code = _wrap(_MEASURE_JS % {"tokens": json.dumps(tokens), "key": key})
        self.browser_js(EDITOR_URL, code, login=user.login, timeout=120)
        self.env.invalidate_all()
        # sudo: reads back a parameter the browser wrote as a system user; the test user may not read it
        raw = self.env["ir.config_parameter"].sudo().get_str(key)
        self.assertTrue(raw, "the editor never reported its palette in the %s scheme" % scheme)
        return json.loads(raw)

    def _hex(self, value):
        return _normalize_colour(value).lower()

    def test_light_editor_wears_the_brand_primary_and_links(self):
        palette = self._measure("light")
        for token, expected in TOKEN_EXPECTATIONS["light"].items():
            with self.subTest(token=token):
                self.assertEqual(self._hex(palette["tokens"][token]), expected)
        for token, value in palette["tokens"].items():
            self.assertNotIn(self._hex(value), LIGHT_ODOO_PURPLE_AND_TEAL, token)

    def test_dark_editor_wears_the_brand_ramp(self):
        palette = self._measure("dark")
        for token, expected in TOKEN_EXPECTATIONS["dark"].items():
            with self.subTest(token=token):
                self.assertEqual(self._hex(palette["tokens"][token]), expected)
        for token, value in palette["tokens"].items():
            self.assertNotIn(self._hex(value), LIGHT_ODOO_PURPLE_AND_TEAL, token)

    def test_primary_button_label_reads_on_every_state_in_both_schemes(self):
        for scheme in ("light", "dark"):
            tokens = self._measure(scheme)["tokens"]
            label = self._hex(tokens["--os-primary-button-text-color"])
            button = self._hex(tokens["--os-primary-button-bg"])
            pairs = {
                "rest": (label, button),
                "hover": (label, self._hex(tokens["--os-primary-button-hover-bg"])),
                # a pressed button shows its fill colour as the label on a pale fill
                "pressed": (button, self._hex(tokens["--os-primary-button-active-bg"])),
            }
            for state, (text, background) in pairs.items():
                with self.subTest(scheme=scheme, state=state):
                    self.assertGreaterEqual(round(_contrast_ratio(text, background), 2), WCAG_AA_NORMAL_TEXT)
            with self.subTest(scheme=scheme, state="link"):
                link = self._hex(tokens["--os-link-color"])
                self.assertGreaterEqual(
                    round(_contrast_ratio(link, self._hex(tokens["--os-white-bg"])), 2), WCAG_AA_NORMAL_TEXT
                )

    def test_dark_chrome_text_is_readable_on_the_brand_ramp(self):
        palette = self._measure("dark")
        for name in ("topbar", "bottombar", "activeSheet"):
            with self.subTest(surface=name):
                surface = palette[name]
                self.assertIsNotNone(surface, "the editor has no %s" % name)
                ratio = _contrast_ratio(self._hex(surface["color"]), self._hex(surface["background"]))
                self.assertGreaterEqual(round(ratio, 2), WCAG_AA_NORMAL_TEXT)
        self.assertEqual(self._hex(palette["activeSheet"]["background"]), "#25383c")
