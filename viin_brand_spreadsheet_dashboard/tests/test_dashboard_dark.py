# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): a dark-scheme user opening the CE Spreadsheet
# Dashboards app (`/odoo/dashboards?dashboard_id=<id>`) sees the dashboard SHELL
# (`.o_spreadsheet_dashboard_action`) repainted as Viindoo's dark app band, while the SHEET
# (the o-spreadsheet canvas grid rendered inside `.o_renderer`) stays exactly what a
# light-scheme user sees, with a visible seam at the boundary between the two, and the
# sidebar's dashboard-list hover state keeps its label readable rather than landing on the
# core stylesheet's near-white palette-ramp hover fill. A light-scheme user sees the CE
# default in every respect - this module's SCSS compiles only into `web.assets_web_dark`.
# The seam rule itself must stay SCOPED to `.o_spreadsheet_dashboard_action` - a dark-scheme
# user's `.o_renderer` anywhere ELSE in the app (any core list/kanban/graph/hierarchy view,
# which all carry the same class) must keep CE's own borderless default; this file guards that
# negative side too, not just the positive in-dashboard seam.
#
# WHY A LIVE BROWSER, NEVER A COMPILED-CSS RESOLVER. The sidebar hover rule
# (`li:hover:not(.active)`) only applies under the browser's own `:hover` pointer state, which
# a page-level `browser_js` script cannot force (a synthetic `dispatchEvent` does not flip a
# real browser's internal `:hover` match). The compiled rule's own declared background is read
# straight off the live `document.styleSheets` CSSOM instead - the exact bundle the browser
# parsed for this page - and composed with the label's own (non-hover) computed colour, so the
# contrast asserted is the one a mouse pointer would actually produce, without depending on a
# pointer to be simulated.
#
# WHY CE'S OWN CLASSES, NEVER A HARDCODED CHROME LITERAL. `.o_renderer`'s own border is read
# live and compared against a plain core `.border` probe element - the same technique the
# sibling `viin_brand_spreadsheet` module's chrome/grid seam assertion uses. The exact border
# colour is this module's own SCSS choice, not a fact this test dictates.
import json

from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools.misc import file_open

from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    _alpha_of,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    dark_palette_var,
)
# Same resolver `test_brand_ssot.py` and `test_brand_cascade_compile.py` already own - reused
# here (rather than re-implemented) to read the LIGHT bundle's own core SSOT below.
from odoo.addons.viin_brand_web.tests.test_brand_ssot import _resolve_scss_hex

# CE's own literal for both plain `background-color: white` declarations in
# `dashboard_action.scss` - the sheet's target colour is simply "stay exactly this", in both
# schemes.
WHITE = "#ffffff"

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
    """Wrap a measurement snippet in the throw/console.error contract `HttpCase.browser_js` polls
    for (`console.log('test successful')` on success, `console.error` on any thrown failure)."""
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


# One page load measures every surface at once: the shell background, the sheet (grid)
# background, the `.o_renderer` border (the seam candidate, compared against a live `.border`
# probe), and the sidebar's compiled hover-fill declaration (read off the CSSOM rather than
# simulated, per the file header). `dashboard_id` is passed as a URL query param, exactly the
# route `spreadsheet_dashboard`'s own `ir_actions_dashboard_action` (path=`dashboards`)
# registers and the action's own `getInitialActiveDashboard()` reads.
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

// The search panel's `li` also carries a SEPARATE, background-less `:hover` rule (revealing the
// per-row edit icon on `.o_search_panel_category_value:hover .o_edit_dashboard`) declared right
// after the one this test targets - matching on bare ":hover" would pick that one up instead
// whenever it happens to compile later. Requiring "li:hover" (the target rule's own compiled
// selector prefix) plus a genuinely declared `background-color` isolates the row-highlight rule.
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
        "premise broken: no compiled CSS rule matches the sidebar row-highlight hover selector - " +
        "the dashboard search panel bundle did not compile as expected."
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


# The leak-guard counterpart to _MEASURE_DASHBOARD_JS above: a CORE list view the dashboard
# action never renders into, so any border this reports comes from a rule that reached
# `.o_renderer` some OTHER way than being inside `.o_spreadsheet_dashboard_action`.
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
    """A dark-scheme user's Spreadsheet Dashboards shell repaints to Viindoo's dark app band
    with a visible seam and a readable sidebar hover label, while the sheet and a light-scheme
    user's whole page stay exactly what CE ships."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Resolved HERE, not as a module-level constant at import time: a class attribute fails
        # only the tests in THIS class if either SSOT source is ever renamed/removed, instead of
        # an import-time exception breaking collection of the whole test module.
        #
        # dashboard_action_dark.dark.scss paints the shell with `$o-webclient-background-color` -
        # resolved from viin_brand_web/static/src/scss/dark_palette.scss (the EXISTING dark
        # app-canvas token this repo already uses for every other "dark app band" surface:
        # viin_backend_theme's home-menu band, the kanban canvas, the settings sidebar) instead of
        # a second hardcoded literal.
        cls.DARK_APP_BAND = dark_palette_var("$o-webclient-background-color")
        # web/static/src/scss/primary_variables.scss `$o-gray-100` (`!default`, never re-pointed
        # by `viin_brand_web`'s dark_palette.scss) - the fixed palette-ramp fill the sidebar's
        # `li:hover:not(.active)` rule reads today (dashboard_action.scss reads it directly, no
        # map indirection). Asserted as the LIGHT bundle's own non-regression value; the dark
        # bundle must resolve its hover fill to something that keeps the label readable instead.
        # `file_open` resolves this core path against the addons path, so it works from any
        # checkout layout, portably - the same technique viin_brand_mail/tests/
        # test_mail_contrast_compile.py already uses to read a core spreadsheet SCSS file.
        with file_open("web/static/src/scss/primary_variables.scss", "r") as core_scss_file:
            cls.LIGHT_HOVER_BG = _resolve_scss_hex(core_scss_file.read(), "$o-gray-100")
        if cls.LIGHT_HOVER_BG is None:
            raise AssertionError(
                "$o-gray-100 must be declared in web/static/src/scss/primary_variables.scss - "
                "the sidebar hover-fill non-regression check reads its expected LIGHT value from "
                "this exact core token."
            )
        cls.LIGHT_HOVER_BG = cls.LIGHT_HOVER_BG.lower()
        # `base.group_system` is granted alongside `base.group_user` here only because the
        # browser-to-Python measurement relay (`__setParam` above) round-trips the captured
        # colours through `ir.config_parameter.set_param`, which `base`'s own
        # `ir.model.access.csv` restricts to `base.group_system` - that requirement belongs to
        # the relay channel, not to the dashboard-shell behaviour these users exist to exercise.
        cls.dark_user = new_test_user(
            cls.env, login="viin_dashboard_dark_user",
            groups="base.group_user,base.group_system", viin_color_scheme="dark",
        )
        cls.light_user = new_test_user(
            cls.env, login="viin_dashboard_light_user",
            groups="base.group_user,base.group_system", viin_color_scheme="light",
        )
        # Created via `cls.env` (superuser in setUpClass), which bypasses both the create-only
        # `spreadsheet_dashboard.group_dashboard_manager` ACL and the `group_ids`/company
        # ir.rule on `spreadsheet.dashboard(.group)` - neither test user needs manager rights to
        # READ a published dashboard, only to create the fixture. `group_ids` and `is_published`
        # are left at their model defaults (`base.group_user`, `True`), the same defaults CE's
        # own `test_create_with_default_values` relies on, so both test users see it unaided.
        cls.dashboard_group = cls.env["spreadsheet.dashboard.group"].create({
            "name": "Viin Brand Dashboard Dark Fixture Group",
        })
        cls.dashboard = cls.env["spreadsheet.dashboard"].create({
            "name": "Viin Brand Dashboard Dark Fixture",
            "dashboard_group_id": cls.dashboard_group.id,
        })
        # Leak-guard fixture: a throwaway CORE list view on `res.partner`, entirely OUTSIDE the
        # Spreadsheet Dashboards action - the same minimal-fixture pattern
        # viin_brand_web/tests/test_scheme_cookie_first_load.py already uses for its pivot/graph
        # fixtures. `.o_list_renderer` (web/static/src/views/list/list_renderer.xml) carries
        # `.o_renderer` alongside it, same as every other core renderer (kanban, graph,
        # hierarchy) - proving whether the dashboard's `.o_renderer` rule leaked into a page the
        # dashboard action never touches.
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
            "premise broken: the browser-side measurement under login %r never reported a "
            "value - the dashboard action must not have reached a mounted state." % login,
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
            "premise broken: the browser-side measurement under login %r never reported a "
            "value - the core list view must not have reached a mounted state." % login,
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
            self.assertIsNotNone(
                dark_hover_bg, "sidebar hover fill: %r carries no readable colour" % dark_hover_bg_raw,
            )
            label_colour_raw = dark["labelColor"]
            label_colour = _normalize_colour(label_colour_raw)
            self.assertIsNotNone(label_colour, "sidebar label: %r carries no readable colour" % label_colour_raw)
            composited_label = _composite_over(label_colour, dark_hover_bg, _alpha_of(label_colour_raw))
            ratio = _contrast_ratio(composited_label, dark_hover_bg)
            self.assertGreaterEqual(
                round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                "the sidebar dashboard-list label %s on its own hover fill %s measures only "
                "%.2f:1, below the WCAG AA normal-text threshold %.1f:1." % (
                    composited_label, dark_hover_bg, ratio, WCAG_AA_NORMAL_TEXT,
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
