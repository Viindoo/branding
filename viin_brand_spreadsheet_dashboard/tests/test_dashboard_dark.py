# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import json

from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools.misc import file_open

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    _alpha_of,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    dark_palette_var,
)
from odoo.addons.viin_brand.tests.test_brand_ssot import _resolve_scss_hex

WHITE = "#ffffff"

# Dark scheme: fill of the dashboard-list row under the pointer and the WCAG contrast of its label.
DARK_HOVER_BG = "#152225"
DARK_HOVER_LABEL_CONTRAST = 14.6

_JS_HELPERS = """
async function __setParam(key, value) {
    const resp = await fetch('/web/dataset/call_kw/ir.config_parameter/set_param', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {model: 'ir.config_parameter', method: 'set_param', args: [key, value], kwargs: {}},
        }),
    });
    const data = await resp.json();
    if (data.error) { throw new Error(JSON.stringify(data.error)); }
}
async function __waitFor(predicate, timeoutMs) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
        const result = predicate();
        if (result) { return result; }
        await new Promise((resolve) => setTimeout(resolve, 100));
    }
    throw new Error('__waitFor: timed out waiting for a condition');
}
function __effectiveBackground(el) {
    let node = el;
    while (node) {
        const bg = getComputedStyle(node).backgroundColor;
        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
            return bg;
        }
        node = node.parentElement;
    }
    return getComputedStyle(document.body).backgroundColor;
}
"""


def _wrap(js_body):
    """Wrap a measurement snippet in the success/failure console contract of ``browser_js``."""
    return _JS_HELPERS + (
        "(async () => {\n"
        "    try {\n"
        "        %s\n"
        "        console.log('test successful');\n"
        "    } catch (e) {\n"
        "        console.error(e && e.stack || e && e.message || String(e));\n"
        "    }\n"
        "})();\n"
    ) % js_body.replace("\n", "\n        ")


# One page load measures the shell background, the sheet (grid) background, the `.o_renderer`
# border (compared against a live `.border` probe) and the sidebar's compiled hover fill, read off
# the CSSOM because a script cannot force the browser's `:hover` state.
_MEASURE_DASHBOARD_JS = """
await __waitFor(() => document.querySelector(".o_spreadsheet_dashboard_action"), 30000);
await __waitFor(() => document.querySelector(".o_renderer .o-spreadsheet .o-grid"), 30000);
const __searchPanelItem = await __waitFor(
    () => document.querySelector(
        '.o_spreadsheet_dashboard_search_panel li[data-name=%(dashboard_name_js)s]'
    ),
    15000
);

const __shell = document.querySelector(".o_spreadsheet_dashboard_action");
const __grid = document.querySelector(".o_renderer .o-spreadsheet .o-grid");
const __renderer = document.querySelector(".o_renderer");
const __label = __searchPanelItem.querySelector(".o_dashboard_name");

const __probe = document.createElement("div");
__probe.className = "border";
__probe.style.position = "absolute";
__probe.style.visibility = "hidden";
document.body.appendChild(__probe);

// The `li` also carries a background-less `:hover` rule (the per-row edit icon); requiring
// "li:hover" plus a declared `background-color` isolates the row-highlight rule.
let __hoverRule = null;
for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch (e) { continue; }
    for (const rule of rules) {
        if (rule.selectorText
            && rule.selectorText.indexOf("li:hover") !== -1
            && rule.style.backgroundColor) {
            __hoverRule = rule;
        }
    }
}
if (!__hoverRule) {
    throw new Error(
        "no compiled CSS rule matches the sidebar row-highlight hover selector"
    );
}

const __result = {
    shellBg: __effectiveBackground(__shell),
    gridBg: __effectiveBackground(__grid),
    rendererBorderColor: getComputedStyle(__renderer).borderTopColor,
    rendererBorderWidth: getComputedStyle(__renderer).borderTopWidth,
    probeBorderColor: getComputedStyle(__probe).borderTopColor,
    labelColor: getComputedStyle(__label).color,
    hoverBg: __hoverRule.style.backgroundColor,
};

await __setParam(%(param_key)r, JSON.stringify(__result));
"""


# A core list view outside the dashboard action: any border it reports leaked from a rule that
# reached `.o_renderer` outside `.o_spreadsheet_dashboard_action`.
_MEASURE_CORE_LIST_JS = """
await __waitFor(() => document.querySelector(".o_list_renderer.o_renderer"), 30000);
const __renderer = document.querySelector(".o_list_renderer.o_renderer");
const __result = {
    rendererBorderWidth: getComputedStyle(__renderer).borderTopWidth,
};
await __setParam(%(param_key)r, JSON.stringify(__result));
"""


@tagged('post_install', '-at_install')
class TestDashboardDark(HttpCase):
    """A dark-scheme user's dashboard shell is Viindoo's dark app band with a seam and a readable hover label.

    The sheet, and a light-scheme user's whole page, stay as CE ships them; the seam rule stays
    scoped to ``.o_spreadsheet_dashboard_action``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DARK_APP_BAND = dark_palette_var("$o-webclient-background-color")
        # Core's `li:hover:not(.active)` rule reads `$o-gray-100`; `file_open` resolves the core path
        # on any addons-path layout.
        with file_open("web/static/src/scss/primary_variables.scss", "r") as core_scss_file:
            cls.LIGHT_HOVER_BG = _resolve_scss_hex(core_scss_file.read(), "$o-gray-100")
        if cls.LIGHT_HOVER_BG is None:
            raise AssertionError(
                "$o-gray-100 must be declared in web/static/src/scss/primary_variables.scss - "
                "the sidebar hover-fill non-regression check reads its expected LIGHT value from "
                "this exact core token."
            )
        cls.LIGHT_HOVER_BG = cls.LIGHT_HOVER_BG.lower()
        # `base.group_system` is needed only by the measurement relay, which stores results through
        # `ir.config_parameter.set_param`.
        cls.dark_user = new_test_user(
            cls.env, login="viin_dashboard_dark_user",
            groups="base.group_user,base.group_system", viin_color_scheme="dark",
        )
        cls.light_user = new_test_user(
            cls.env, login="viin_dashboard_light_user",
            groups="base.group_user,base.group_system", viin_color_scheme="light",
        )
        # Defaults of `group_ids` and `is_published` let both users read the dashboard unaided.
        cls.dashboard_group = cls.env["spreadsheet.dashboard.group"].create({
            "name": "Viin Brand Dashboard Dark Fixture Group",
        })
        cls.dashboard = cls.env["spreadsheet.dashboard"].create({
            "name": "Viin Brand Dashboard Dark Fixture",
            "dashboard_group_id": cls.dashboard_group.id,
        })
        # Leak guard: a core list view outside the dashboard action; `.o_list_renderer` carries
        # `.o_renderer` like every core renderer.
        cls.core_list_view = cls.env["ir.ui.view"].create({
            "name": "Viin Brand Dashboard Dark Leak-Guard List (test)",
            "model": "res.partner",
            "type": "list",
            "arch": "<list/>",
        })
        cls.core_list_action = cls.env["ir.actions.act_window"].create({
            "name": "Viin Brand Dashboard Dark Leak-Guard List (test)",
            "res_model": "res.partner",
            "view_mode": "list",
            "view_id": cls.core_list_view.id,
        })

    def setUp(self):
        super().setUp()
        if "tour_enabled" not in self.env["res.users"]._fields:
            self.skipTest("web_tour is not installed")

    def _measure(self, login):
        param_key = "viin_brand_spreadsheet_dashboard.dark_test.%s" % login
        code = _wrap(_MEASURE_DASHBOARD_JS % {
            "dashboard_name_js": json.dumps(self.dashboard.name),
            "param_key": param_key,
        })
        self.browser_js(
            "/odoo/dashboards?dashboard_id=%d" % self.dashboard.id, code, login=login, timeout=120,
        )
        self.env.invalidate_all()
        raw = self.env["ir.config_parameter"].sudo().get_param(param_key)
        self.assertTrue(
            raw,
            "the browser measurement under login %r reported no value - the dashboard action "
            "did not mount." % login,
        )
        return json.loads(raw)

    def _measure_core_list(self, login):
        param_key = "viin_brand_spreadsheet_dashboard.dark_test.core_list.%s" % login
        code = _wrap(_MEASURE_CORE_LIST_JS % {"param_key": param_key})
        self.browser_js(
            "/odoo/action-%d" % self.core_list_action.id, code, login=login, timeout=120,
        )
        self.env.invalidate_all()
        raw = self.env["ir.config_parameter"].sudo().get_param(param_key)
        self.assertTrue(
            raw,
            "the browser measurement under login %r reported no value - the core list view "
            "did not mount." % login,
        )
        return json.loads(raw)

    def test_dashboard_shell_follows_color_scheme_sheet_and_hover_stay_correct(self):
        dark = self._measure(self.dark_user.login)
        light = self._measure(self.light_user.login)

        with self.subTest(surface="shell background"):
            dark_shell = _normalize_colour(dark["shellBg"])
            light_shell = _normalize_colour(light["shellBg"])
            self.assertIsNotNone(dark_shell, "dashboard shell: %r carries no readable colour" % dark["shellBg"])
            self.assertEqual(
                dark_shell, self.DARK_APP_BAND,
                "a dark-scheme user's dashboard shell (.o_spreadsheet_dashboard_action) resolves "
                "to %s, not the app's own dark band %s - the shell never repainted." % (
                    dark_shell, self.DARK_APP_BAND,
                ),
            )
            self.assertEqual(
                light_shell, WHITE,
                "a light-scheme user's dashboard shell must keep CE's own white background - "
                "this module's SCSS must not compile into the light bundle.",
            )

        with self.subTest(surface="sheet (grid) background"):
            dark_grid = _normalize_colour(dark["gridBg"])
            light_grid = _normalize_colour(light["gridBg"])
            self.assertIsNotNone(dark_grid, "sheet grid: %r carries no readable colour" % dark["gridBg"])
            self.assertEqual(
                dark_grid, WHITE,
                "the sheet (.o-grid) must stay CE's own white under a dark-scheme user - it "
                "resolves to %s instead." % dark_grid,
            )
            self.assertEqual(
                dark_grid, light_grid,
                "the sheet must render IDENTICALLY for a dark-scheme user (%s) and a "
                "light-scheme user (%s) - no dark rule may reach the o-spreadsheet canvas." % (
                    dark_grid, light_grid,
                ),
            )

        with self.subTest(surface="shell/sheet seam"):
            probe_colour = _normalize_colour(dark["probeBorderColor"])
            self.assertIsNotNone(probe_colour, "the .border probe carries no readable border colour")
            self.assertNotEqual(
                dark["rendererBorderWidth"], "0px",
                ".o_renderer renders no border at all for a dark-scheme user - there is no "
                "visible seam between the dark shell and the light sheet.",
            )
            renderer_border = _normalize_colour(dark["rendererBorderColor"])
            self.assertEqual(
                renderer_border, probe_colour,
                ".o_renderer's border resolves to %s, not the current theme's border colour %s "
                "a plain core `.border` element resolves to." % (renderer_border, probe_colour),
            )
            self.assertEqual(
                light["rendererBorderWidth"], "0px",
                "a light-scheme user must keep CE's own borderless .o_renderer - this module's "
                "SCSS must not compile into the light bundle.",
            )

        with self.subTest(surface="sidebar dashboard-list hover fill"):
            light_hover_bg = _normalize_colour(light["hoverBg"])
            self.assertEqual(
                light_hover_bg, self.LIGHT_HOVER_BG,
                "a light-scheme user's sidebar hover fill must stay CE's own %s - this module's "
                "SCSS must not compile into the light bundle." % self.LIGHT_HOVER_BG,
            )
            dark_hover_bg_raw = dark["hoverBg"]
            dark_hover_bg = _normalize_colour(dark_hover_bg_raw)
            self.assertEqual(
                dark_hover_bg, DARK_HOVER_BG,
                "a dark-scheme user's sidebar dashboard row under the pointer resolves to %s, not "
                "the pinned %s." % (dark_hover_bg_raw, DARK_HOVER_BG),
            )
            label_colour_raw = dark["labelColor"]
            label_colour = _normalize_colour(label_colour_raw)
            self.assertIsNotNone(label_colour, "sidebar label: %r carries no readable colour" % label_colour_raw)
            composited_label = _composite_over(label_colour, dark_hover_bg, _alpha_of(label_colour_raw))
            ratio = _contrast_ratio(composited_label, dark_hover_bg)
            self.assertEqual(
                round(ratio, 1), DARK_HOVER_LABEL_CONTRAST,
                "the sidebar dashboard-list label %s on its hover fill %s measures %.2f:1, not the "
                "pinned %.1f:1." % (
                    composited_label, dark_hover_bg, ratio, DARK_HOVER_LABEL_CONTRAST,
                ),
            )

    def test_o_renderer_border_stays_scoped_to_dashboard_action_for_dark_user(self):
        dark_core_list = self._measure_core_list(self.dark_user.login)
        light_core_list = self._measure_core_list(self.light_user.login)
        self.assertEqual(
            dark_core_list["rendererBorderWidth"], light_core_list["rendererBorderWidth"],
            "a dark-scheme user's core list view (.o_list_renderer.o_renderer), opened OUTSIDE "
            "the Spreadsheet Dashboards action, resolves a %r border while a light-scheme user's "
            "SAME core list view resolves %r - the dashboard's .o_renderer seam rule leaked into "
            "every .o_renderer in the app instead of staying scoped to "
            ".o_spreadsheet_dashboard_action." % (
                dark_core_list["rendererBorderWidth"], light_core_list["rendererBorderWidth"],
            ),
        )
