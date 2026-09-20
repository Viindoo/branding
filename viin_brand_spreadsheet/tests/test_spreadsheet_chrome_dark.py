# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): a dark-scheme user opening the CE spreadsheet editor
# sees the COMMAND CHROME - the menu bar / toolbar / formula bar
# (`.o-spreadsheet-topbar-wrapper`) and the sheet-tab bar (`.o-spreadsheet-bottombar-wrapper`) -
# repainted dark with readable labels, while the DOCUMENT ZONE (the canvas grid, the side panel,
# a chart figure's own header, the filter-menu popover) renders BYTE-IDENTICAL to a light-scheme
# user - never re-pointed by this module. The seam between the grid and the chrome resolves to
# the same colour a plain core `.border` utility resolves to elsewhere on the page. A Chatter
# mounted in the side panel keeps its muted text readable once composited over each element's own
# real rendered background. The toolbar icons inside the dark chrome (`.o-hoverable-button
# .o-icon`) stay readable against the chrome's own dark background.
# Three surfaces stay LIGHT ISLANDS regardless of scheme, exactly like the grid/side-panel/popovers
# above - the formula-bar composer, the mobile small-bottom-bar composer, and the mobile ribbon
# menu - each readable against its OWN real (white) background, never the chrome's dark one. A
# link-style button rendered inside any of these light islands stays readable in its pressed state
# too, for both a dark-scheme and a light-scheme user.
#
# WHY A LIVE BROWSER, NEVER A COMPILED-CSS RESOLVER. `spreadsheet/static/src/o_spreadsheet/
# o_spreadsheet.js` builds its own chrome/island CSS from JS string constants and appends it to
# `document.head` as `<style>` tags at RUNTIME, after every bundle `<link>` - it is not part of
# any SCSS this module or core ships, so no compiled-bundle reader can see it (confirmed by
# reading the generated file directly: the `.o-spreadsheet .text-muted { color: ... !important }`
# pin lives inside a JS `css` tagged template, not a `.scss` source). Every value below is read
# with `getComputedStyle` against the real, rendered cascade.
#
# WHY CE'S OWN CLASSES, NEVER A HARDCODED CHROME LITERAL. The exact dark tone the chrome repaints
# to is this module's own SCSS choice (an OPL-1 lever, not a fact this test dictates), so "is
# dark" is asserted as an OUTCOME (materially different from - and darker than - the same surface
# under a light-scheme user, with every label still >= 4.5:1 on it) rather than as an assertEqual
# on one hand-picked hex. Where the AC is instead an EQUALITY - the document zone must stay
# byte-identical between the two schemes, the seam must equal a live `.border` probe - the test
# measures BOTH sides live and compares them, never a value copied out of a design note.
#
# WHY A TEST-ONLY CLIENT ACTION. CE's spreadsheet addon registers no editor action of its own
# outside a business module's data (only a download action, a lazy-bundle loader and the
# dashboard action - confirmed by reading `spreadsheet/static/src/assets_backend/*.js` and
# `spreadsheet/static/src/actions/*.js` in full), so there is no core route into a rendered
# editor. `static/tests/tours/test_spreadsheet_editor_action.js` (web.assets_tests) is that route:
# CORE classes only (`SpreadsheetComponent`, `Model`, the engine's own store registry) - never an
# `o_viin_*` / business-module selector, so this fixture keeps mounting a bare CE editor even on a
# checkout with no business module installed at all.
import json

from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools.misc import file_open

from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    WCAG_NON_TEXT_MIN,
    _alpha_of,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    _relative_luminance,
)
from odoo.addons.viin_brand_web.tests.test_brand_ssot import _resolve_scss_hex

# The bare registry TAG the test-only client action self-registers under
# (static/tests/tours/test_spreadsheet_editor_action.js `VIIN_TEST_SPREADSHEET_EDITOR_ACTION_TAG`)
# - a plain string `doAction()` resolves against the client-action registry with zero server
# round-trip (web/static/src/webclient/actions/action_service.js `_loadAction`), exactly like
# core's own registry-only actions (e.g. "action_download_spreadsheet").
TEST_EDITOR_ACTION_TAG = "viin_brand_spreadsheet_chrome_dark_test_editor"

# A generous upper bound on "reads as a dark surface": Viindoo's own dark panel tokens sit near
# 0.0 (`#111b1e` ~= 0.006); CE's stock light chrome sits near 1.0 (a white/near-white ground). A
# surface has repainted dark only if BOTH this bound holds AND it differs from the same surface
# under a light-scheme user - the two checks together are what make this a behaviour assertion
# rather than a "not exactly white" one a translucent shadow could also satisfy.
DARK_CHROME_MAX_RELATIVE_LUMINANCE = 0.4

# core's own SSOT for $os-text-body (o_spreadsheet_variables.scss) - resolved live off the addons
# path rather than copied as a literal, so a core re-tune of the variable keeps every assertion
# below correct instead of silently drifting from a stale hardcoded copy.
CORE_SPREADSHEET_VARIABLES_SCSS = "spreadsheet/static/src/o_spreadsheet/o_spreadsheet_variables.scss"

_core_os_text_body_cache = {}


def _core_os_text_body():
    """Return the hex `$os-text-body` resolves to in `CORE_SPREADSHEET_VARIABLES_SCSS`, or None
    if the variable can no longer be found there."""
    if "hex" not in _core_os_text_body_cache:
        with file_open(CORE_SPREADSHEET_VARIABLES_SCSS, "r") as core_file:
            content = core_file.read()
        _core_os_text_body_cache["hex"] = _normalize_colour(_resolve_scss_hex(content, "$os-text-body"))
    return _core_os_text_body_cache["hex"]


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


# One continuous browser session drives: mount the editor -> measure the chrome (row 1) -> create
# a carousel figure and select it (so its own side panel/carousel-header render) -> open the
# engine's OWN filter-menu popover -> measure the document zone (row 2) -> mount a core Chatter in
# the now-open side panel (row 3) -> measure the grid/chrome seam against a live `.border` probe
# (row 4). Every DOM query and store call below is a CORE class or a CORE store
# (`stores.SidePanelStore`, `stores.CellPopoverStore`, both re-exported by `@odoo/o-spreadsheet`) -
# never a business-module selector.
#
# Toolbar icon + formula-bar composer (added alongside the rows above, same mounted editor, no
# extra browser session): every default (non-readonly) toolbar action AND the "more tools"
# chevron (`.o-toolbar-button.o-hoverable-button.more-tools`, top_bar.xml, rendered
# UNCONDITIONALLY - a guaranteed fallback match even if the registry-driven actions before it were
# ever empty) share the class `.o-hoverable-button`; whichever one document order picks first,
# its `.o-icon` is an `fill="currentColor"` `<svg>`, so its rendered ink IS
# `getComputedStyle(...).color`, governed by the engine's single, UN-scoped
# `.o-hoverable-button .o-icon { color: TEXT_BODY }` rule (o_spreadsheet.js). That rule has no
# bottombar-specific counterpart for this file to cover: reading the full generated
# `o-spreadsheet-BottomBar` / `BottomBarStatistic` / `BottomBarSheet` templates found them
# rendering NO `.o-hoverable-button` anywhere, by default or otherwise. So this file measures the
# ONE real element the rule ever applies to - the topbar's - against the topbar's own background;
# it does not, and cannot, cover a bottombar icon rule that has no element to apply to.
# `.o-topbar-composer` (`TopBarComposer`, o_spreadsheet.xml) carries CE's own `bg-white`, forced
# `!important` by core's OWN `o_spreadsheet_extended.dark.scss` - a LIGHT ISLAND this module must
# never re-point; its inner `.o-composer` sets no `color` of its own, so it inherits whatever this
# module's chrome rule paints the wrapper's text - which is exactly the risk a light-island
# assertion here exists to catch.
_MEASURE_EDITOR_JS = """
const __wowlDebug = await __waitFor(
    () => window.odoo.__WOWL_DEBUG__ && window.odoo.__WOWL_DEBUG__.root, 30000
);
const __env = __wowlDebug.env;
await __env.services.action.doAction(%(action_tag)r);
await __waitFor(() => document.querySelector(".o-spreadsheet-topbar-wrapper"), 30000);
const __test = await __waitFor(() => window.__viinBrandSpreadsheetChromeDarkTest, 30000);
const { model, stores, getStore } = __test;

const __topbarWrapper = document.querySelector(".o-spreadsheet-topbar-wrapper");
const __bottombarWrapper = document.querySelector(".o-spreadsheet-bottombar-wrapper");
const __topbarLabel = await __waitFor(
    () => Array.from(document.querySelectorAll(".o-topbar-menu")).find(
        (el) => el.textContent.trim().length > 0
    ),
    15000
);
const __sheetLabel = await __waitFor(() => document.querySelector(".o-sheet-name"), 15000);
const __gridContainer = document.querySelector(".o-grid-container");
const __toolbarIcon = await __waitFor(
    () => __topbarWrapper.querySelector(".o-hoverable-button:not(.active) .o-icon"), 15000
);
const __topbarComposerInput = await __waitFor(
    () => __topbarWrapper.querySelector(".o-topbar-composer .o-composer"), 15000
);

const __sheetId = model.getters.getActiveSheetId();
const __figureId = %(figure_id)r;
const __carouselResult = model.dispatch("CREATE_CAROUSEL", {
    sheetId: __sheetId,
    figureId: __figureId,
    col: 0,
    row: 0,
    offset: { x: 0, y: 0 },
    size: { width: 536, height: 335 },
    definition: { items: [] },
});
if (!__carouselResult.isSuccessful) {
    throw new Error("CREATE_CAROUSEL was rejected: " + JSON.stringify(__carouselResult.reasons));
}
model.dispatch("SELECT_FIGURE", { figureId: __figureId });
getStore(stores.SidePanelStore).open("CarouselPanel", { figureId: __figureId });
const __sidePanel = await __waitFor(() => document.querySelector(".o-sidePanel"), 15000);
const __carouselHeader = await __waitFor(() => document.querySelector(".o-carousel-header"), 15000);

getStore(stores.CellPopoverStore).open({ col: 0, row: 0 }, "FilterMenu");
const __filterMenu = await __waitFor(() => document.querySelector(".o-filter-menu"), 15000);

const __result = {
    topbarBg: __effectiveBackground(__topbarWrapper),
    bottombarBg: __effectiveBackground(__bottombarWrapper),
    topbarLabelColor: getComputedStyle(__topbarLabel).color,
    sheetLabelColor: getComputedStyle(__sheetLabel).color,
    gridBg: __effectiveBackground(__gridContainer),
    sidePanelBg: __effectiveBackground(__sidePanel),
    carouselHeaderBg: __effectiveBackground(__carouselHeader),
    filterMenuBg: __effectiveBackground(__filterMenu),
    topbarSeamColor: getComputedStyle(__topbarWrapper).borderBottomColor,
    bottombarSeamColor: getComputedStyle(__bottombarWrapper).borderTopColor,
    toolbarIconColor: getComputedStyle(__toolbarIcon).color,
    topbarComposerBg: __effectiveBackground(__topbarComposerInput),
    topbarComposerColor: getComputedStyle(__topbarComposerInput).color,
};

%(chatter_js)s

await __setParam(%(param_key)r, JSON.stringify(__result));
"""

# Mounts a core Chatter (Composer included) on a test-created `res.partner` inside the side panel
# the carousel flow above already opened, then measures the muted text - the surface the engine's
# own injected `.o-spreadsheet .text-muted` pin (o_spreadsheet.js) governs - AGAINST its own real
# rendered background (`__effectiveBackground`), never an assumed literal: the side panel itself
# is white, but an element can still paint its OWN background regardless of what the panel
# underneath renders. Also measures the "follow" toggle button (`.o-mail-Followers-button`, a real
# `.btn.btn-link`, chatter.xml) in its PRESSED state -
# read via `--btn-active-color` directly off the element rather than faking `:active` (a
# synthetic DOM event never flips a real browser's `:active` match; this button is genuinely its
# parent's only/first child, so Bootstrap's own `.btn:first-child:active` rule - sharing the exact
# same `color: var(--btn-active-color)` declaration as a real pointer-press - already governs
# it today, no simulated press needed to read the value that rule would apply).
_CHATTER_JS = """
const __probe = document.createElement("div");
__probe.className = "border";
__probe.style.position = "absolute";
__probe.style.visibility = "hidden";
document.body.appendChild(__probe);
__result.probeBorderColor = getComputedStyle(__probe).borderTopColor;

const __owl = odoo.loader.modules.get("@odoo/owl");
const __chatterModule = odoo.loader.modules.get("@mail/chatter/web_portal/chatter");
// `Chatter`'s own template is a QWeb XML asset resolved BY NAME - only the webclient's own
// root App wires that lookup in, via the `getTemplate` App option (web/static/src/env.js
// imports it from this same module and passes it to `new App(...)`). This standalone mount
// creates its OWN App, so it must supply the same option or OWL's default (inline `xml`-tag
// templates only) cannot resolve "mail.Chatter" - the exact mechanism CE's own mail module
// uses for a standalone mount outside the webclient (mail_popout_service.js). The module is
// part of the always-eager web.assets_backend bundle (web/static/src/env.js itself imports it,
// and env.js cannot have run without it), so reading it synchronously here is race-free.
const { getTemplate } = odoo.loader.modules.get("@web/core/templates");
const __chatterHost = document.createElement("div");
__sidePanel.appendChild(__chatterHost);
await __owl.mount(__chatterModule.Chatter, __chatterHost, {
    env: __env,
    getTemplate,
    props: { threadId: %(partner_id)d, threadModel: "res.partner", composer: true },
});
const __chatterMuted = await __waitFor(() => __chatterHost.querySelector(".text-muted"), 15000);
const __followersButton = await __waitFor(
    () => __chatterHost.querySelector(".o-mail-Followers-button"), 15000
);
__result.chatterMutedColor = getComputedStyle(__chatterMuted).color;
__result.chatterMutedBg = __effectiveBackground(__chatterMuted);
__result.followersButtonBg = __effectiveBackground(__followersButton);
__result.followersButtonActiveColor = getComputedStyle(__followersButton)
    .getPropertyValue("--btn-active-color")
    .trim();
"""

# Toggles the engine's OWN "View > Irregularity map" menu item via a REAL click on the exact path
# a user takes - the topbar menu button, then its popover item (`topbarMenuRegistry` ids `view` /
# `view_irregularity_map`, o_spreadsheet.js) - never a store mutator called by hand, the same
# real-DOM-click technique this file already uses below for `__ribbonToggler`. That menu item's
# own `execute()` toggles `FormulaFingerprintStore.isEnabled`, which mounts `.irregularity-map`
# (o_spreadsheet.xml, `t-if="this.fingerprints.isEnabled"`) directly on the dark topbar chrome -
# OUTSIDE every light island (`.o-sidePanel` / `.o-popover`) the rows above measure. Its "Turn
# off" `.btn-link` (the only `.btn-link` this subtree ever renders) is read the same way the
# Chatter follow-toggle above is: `--btn-active-color` straight off the element, no synthetic
# `:active` needed, for the same reason given above. Only the raw override value is captured -
# this surface's own background/contrast is not composited here, since certifying it is outside
# what this module's lever owns (see the test docstring below).
# Reused via the `_measure()` `chatter_js` extension slot (any extra JS run after the base
# `__result` is assembled) - the parameter name is a historical artefact of its original purpose,
# not a constraint on what it may carry.
_IRREGULARITY_MAP_JS = """
const __viewMenuButton = await __waitFor(
    () => __topbarWrapper.querySelector('.o-topbar-menu[data-id="view"]'), 15000
);
__viewMenuButton.click();
const __irregularityMenuItem = await __waitFor(
    () => document.querySelector('.o-menu-item[data-name="view_irregularity_map"]'), 15000
);
__irregularityMenuItem.click();
const __irregularityTurnOff = await __waitFor(
    () => document.querySelector(".irregularity-map .btn-link"), 15000
);
__result.irregularityTurnOffActiveColor = getComputedStyle(__irregularityTurnOff)
    .getPropertyValue("--btn-active-color")
    .trim();
"""

# Mounts the editor under a NARROWED emulated viewport (see `_measure_mobile` below) so the
# engine's OWN `useScreenWidth()` hook (`spreadsheetRect.width < 768`, o_spreadsheet.js) flips
# `env.isSmall` true and swaps `TopBarComposer`/`BottomBar` for `SmallBottomBar`/`RibbonMenu` -
# the exact mechanism the engine itself uses for its mobile layout, never a viewport this test
# invents. `.o-small-composer` is the mobile formula-bar equivalent, present by default;
# `.o-menu` (the ribbon) only mounts after a genuine click on `.ribbon-toggler` - a REAL DOM
# click fires the component's own `t-on-click` listener correctly (unlike `:hover`/`:active`,
# a click is a discrete event, not an ongoing pointer state a synthetic dispatch cannot fake).
# `.bottom-bar-menu` (o_spreadsheet.xml `o-spreadsheet-SmallBottomBar`) only renders in the SAME
# `menuState.isOpen === false` branch the ribbon toggler click flips away from, so its border and
# the mobile topbar-wrapper's own box-shadow are both read BEFORE that click - the two surfaces
# core's own `.o-spreadsheet.o-spreadsheet-mobile .o-spreadsheet-topbar-wrapper` glow rule and
# `.o-spreadsheet-small-bottom-bar .bottom-bar-menu` border rule (o_spreadsheet.scss) paint,
# neither yet re-pointed by this module's mobile chrome.
_MEASURE_MOBILE_JS = """
const __wowlDebug = await __waitFor(
    () => window.odoo.__WOWL_DEBUG__ && window.odoo.__WOWL_DEBUG__.root, 30000
);
const __env = __wowlDebug.env;
await __env.services.action.doAction(%(action_tag)r);
const __topbarWrapper = await __waitFor(
    () => document.querySelector(".o-spreadsheet-topbar-wrapper"), 30000
);
const __bottombarWrapper = await __waitFor(
    () => document.querySelector(".o-spreadsheet-bottombar-wrapper"), 30000
);
const __smallComposer = await __waitFor(
    () => __bottombarWrapper.querySelector(".o-small-composer .o-composer"), 15000
);
const __bottomBarMenu = await __waitFor(
    () => __bottombarWrapper.querySelector(".bottom-bar-menu"), 15000
);

const __probe = document.createElement("div");
__probe.className = "border";
__probe.style.position = "absolute";
__probe.style.visibility = "hidden";
document.body.appendChild(__probe);

const __result = {
    smallComposerBg: __effectiveBackground(__smallComposer),
    smallComposerColor: getComputedStyle(__smallComposer).color,
    topbarWrapperBoxShadow: getComputedStyle(__topbarWrapper).boxShadow,
    bottomBarMenuBorderColor: getComputedStyle(__bottomBarMenu).borderTopColor,
    probeBorderColor: getComputedStyle(__probe).borderTopColor,
};

const __ribbonToggler = await __waitFor(
    () => __bottombarWrapper.querySelector(".ribbon-toggler"), 15000
);
__ribbonToggler.click();
const __ribbonMenu = await __waitFor(() => __bottombarWrapper.querySelector(".o-menu"), 15000);
const __ribbonMenuItemName = await __waitFor(
    () => __ribbonMenu.querySelector(".o-menu-item-name"), 15000
);
__result.ribbonMenuBg = __effectiveBackground(__ribbonMenu);
__result.ribbonMenuItemColor = getComputedStyle(__ribbonMenuItemName).color;

await __setParam(%(param_key)r, JSON.stringify(__result));
"""


@tagged("post_install", "-at_install")
class TestSpreadsheetChromeDark(HttpCase):
    """The CE spreadsheet editor's command chrome follows a dark-scheme user while its document
    zone - grid, side panel, chart-figure header, filter-menu popover - stays exactly what a
    light-scheme user sees, and a Chatter mounted in the side panel stays readable."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `base.group_system` is granted alongside `base.group_user` here only because the
        # browser-to-Python measurement relay (`__setParam` above) round-trips the captured
        # colours through `ir.config_parameter.set_param`, which `base`'s own
        # `ir.model.access.csv` restricts to `base.group_system` - that requirement belongs to
        # the relay channel, not to the dark-chrome behaviour these users exist to exercise.
        cls.dark_user = new_test_user(
            cls.env, login="viin_spreadsheet_chrome_dark_user",
            groups="base.group_user,base.group_system", viin_color_scheme="dark",
        )
        cls.light_user = new_test_user(
            cls.env, login="viin_spreadsheet_chrome_light_user",
            groups="base.group_user,base.group_system", viin_color_scheme="light",
        )
        cls.partner = cls.env["res.partner"].create({
            "name": "Spreadsheet Chrome Dark Chatter Fixture Partner",
        })

    def setUp(self):
        super().setUp()
        if "tour_enabled" not in self.env["res.users"]._fields:
            self.skipTest("web_tour is not installed")

    def _measure(self, login, figure_id, chatter_js=""):
        param_key = "viin_brand_spreadsheet.chrome_dark_test.%s" % login
        code = _wrap(_MEASURE_EDITOR_JS % {
            "action_tag": TEST_EDITOR_ACTION_TAG,
            "figure_id": figure_id,
            "chatter_js": chatter_js,
            "param_key": param_key,
        })
        self.browser_js("/odoo", code, login=login, timeout=180)
        self.env.invalidate_all()
        raw = self.env["ir.config_parameter"].sudo().get_param(param_key)
        self.assertTrue(
            raw,
            "premise broken: the browser-side measurement under login %r never reported a "
            "value - the test editor action must not have reached a mounted state." % login,
        )
        return json.loads(raw)

    def _measure_mobile(self, login):
        param_key = "viin_brand_spreadsheet.chrome_dark_mobile_test.%s" % login
        code = _wrap(_MEASURE_MOBILE_JS % {
            "action_tag": TEST_EDITOR_ACTION_TAG,
            "param_key": param_key,
        })
        # `browser_size` (base HttpCase attribute, default "1366x768") drives the Chrome
        # `Emulation.setDeviceMetricsOverride` call a fresh `ChromeBrowser` reads at the START of
        # every `browser_js()` call (odoo/tests/common.py) - narrowing it here, then restoring it,
        # forces the ONE real signal the engine's own mobile breakpoint reads
        # (`.o-spreadsheet`'s rendered width) without touching any test-only flag the engine
        # itself does not consult.
        original_browser_size = self.browser_size
        self.browser_size = "375,700"
        try:
            self.browser_js("/odoo", code, login=login, timeout=180)
        finally:
            self.browser_size = original_browser_size
        self.env.invalidate_all()
        raw = self.env["ir.config_parameter"].sudo().get_param(param_key)
        self.assertTrue(
            raw,
            "premise broken: the browser-side mobile measurement under login %r never reported "
            "a value - narrowing the viewport must not have flipped the engine's own `isSmall` "
            "breakpoint, so `.o-small-composer` never mounted." % login,
        )
        return json.loads(raw)

    def test_dark_scheme_gets_readable_chrome_light_scheme_stays_untouched(self):
        dark = self._measure(
            self.dark_user.login, "viin-chrome-dark-test-carousel",
            chatter_js=_CHATTER_JS % {"partner_id": self.partner.id},
        )
        light = self._measure(
            self.light_user.login, "viin-chrome-light-test-carousel",
            chatter_js=_CHATTER_JS % {"partner_id": self.partner.id},
        )

        # -- Row 1: the chrome repaints dark, with every label readable on it -------------------
        for surface, bg_key, label_key in (
            ("topbar (menu bar / toolbar / formula bar)", "topbarBg", "topbarLabelColor"),
            ("bottombar (sheet tabs)", "bottombarBg", "sheetLabelColor"),
        ):
            with self.subTest(surface=surface):
                dark_bg = _normalize_colour(dark[bg_key])
                light_bg = _normalize_colour(light[bg_key])
                self.assertIsNotNone(dark_bg, "%s: %r carries no readable colour" % (surface, dark[bg_key]))
                self.assertIsNotNone(light_bg, "%s: %r carries no readable colour" % (surface, light[bg_key]))
                self.assertNotEqual(
                    dark_bg, light_bg,
                    "%s: a dark-scheme user renders the SAME background %s a light-scheme user "
                    "does - the chrome never repainted." % (surface, dark_bg),
                )
                luminance = _relative_luminance(dark_bg)
                self.assertLessEqual(
                    round(luminance, 3), DARK_CHROME_MAX_RELATIVE_LUMINANCE,
                    "%s: dark-scheme background %s has relative luminance %.3f, above the %.1f "
                    "bound a dark surface must sit under." % (
                        surface, dark_bg, luminance, DARK_CHROME_MAX_RELATIVE_LUMINANCE,
                    ),
                )
                label_colour = _normalize_colour(dark[label_key])
                self.assertIsNotNone(label_colour, "%s label: %r carries no readable colour" % (surface, dark[label_key]))
                ratio = _contrast_ratio(label_colour, dark_bg)
                self.assertGreaterEqual(
                    round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                    "%s label %s on its own dark background %s measures only %.2f:1, below the "
                    "WCAG AA normal-text threshold %.1f:1." % (
                        surface, label_colour, dark_bg, ratio, WCAG_AA_NORMAL_TEXT,
                    ),
                )

        # -- Toolbar icon: the engine's single UN-scoped `.o-hoverable-button .o-icon` rule reads
        # as dark-chrome text against the topbar's own dark background - the only wrapper this
        # rule has a real element to apply to (the bottombar renders no `.o-hoverable-button` at
        # all, so there is no bottombar-specific instance of this rule for this file to cover) ----
        icon_colour = _normalize_colour(dark["toolbarIconColor"])
        self.assertIsNotNone(icon_colour, "toolbar icon: %r carries no readable colour" % dark["toolbarIconColor"])
        for surface, bg_key in (
            ("topbar toolbar icon", "topbarBg"),
        ):
            with self.subTest(surface=surface):
                chrome_bg = _normalize_colour(dark[bg_key])
                self.assertIsNotNone(chrome_bg, "%s: %r carries no readable colour" % (surface, dark[bg_key]))
                ratio = _contrast_ratio(icon_colour, chrome_bg)
                self.assertGreaterEqual(
                    round(ratio, 2), WCAG_NON_TEXT_MIN,
                    "%s %s on its own dark chrome background %s measures only %.2f:1, below the "
                    "WCAG 1.4.11 non-text threshold %.1f:1." % (
                        surface, icon_colour, chrome_bg, ratio, WCAG_NON_TEXT_MIN,
                    ),
                )

        # -- Formula-bar composer: a LIGHT ISLAND (CE's own forced `bg-white`) - readable against
        # its OWN real background, never the chrome's dark one, for the dark-scheme user ----------
        with self.subTest(surface="formula bar (.o-topbar-composer)"):
            composer_bg = _normalize_colour(dark["topbarComposerBg"])
            self.assertIsNotNone(
                composer_bg, "formula bar: %r carries no readable colour" % dark["topbarComposerBg"],
            )
            raw_composer_fg = dark["topbarComposerColor"]
            composer_fg = _normalize_colour(raw_composer_fg)
            self.assertIsNotNone(composer_fg, "formula bar label: %r carries no readable colour" % raw_composer_fg)
            composited = _composite_over(composer_fg, composer_bg, _alpha_of(raw_composer_fg))
            ratio = _contrast_ratio(composited, composer_bg)
            self.assertGreaterEqual(
                round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                "formula bar label %s on its own real background %s measures only %.2f:1, below "
                "the WCAG AA normal-text threshold %.1f:1 - a light island must stay readable "
                "against its OWN background, not the dark chrome's." % (
                    composited, composer_bg, ratio, WCAG_AA_NORMAL_TEXT,
                ),
            )

        # -- Row 5 (light-scheme non-regression): the label keeps CE's own stock colour ---------
        core_os_text_body = _core_os_text_body()
        self.assertIsNotNone(
            core_os_text_body,
            "%s must assign a hex to $os-text-body (directly or via a $var), so this test can "
            "compare against the live SSOT instead of a hardcoded literal." % CORE_SPREADSHEET_VARIABLES_SCSS,
        )
        self.assertEqual(
            _normalize_colour(light["topbarLabelColor"]), core_os_text_body,
            "a light-scheme user's topbar label must keep rendering the engine's own "
            "$os-text-body colour (%s) - this module must not touch it." % core_os_text_body,
        )

        # -- Row 2: the document zone is byte-identical between the two schemes -----------------
        for surface, key in (
            (".o-grid-container (canvas grid)", "gridBg"),
            (".o-sidePanel (side panel)", "sidePanelBg"),
            (".o-carousel-header (chart figure header)", "carouselHeaderBg"),
            (".o-filter-menu (filter popover)", "filterMenuBg"),
        ):
            with self.subTest(surface=surface):
                dark_value = _normalize_colour(dark[key])
                light_value = _normalize_colour(light[key])
                self.assertIsNotNone(dark_value, "%s: %r carries no readable colour" % (surface, dark[key]))
                self.assertEqual(
                    dark_value, light_value,
                    "%s must render IDENTICALLY for a dark-scheme user (%s) and a light-scheme "
                    "user (%s) - this is document zone, no $os-* re-point may reach it." % (
                        surface, dark_value, light_value,
                    ),
                )

        # -- Row 4: the grid/chrome seam equals a live core `.border` probe ---------------------
        probe_colour = _normalize_colour(dark["probeBorderColor"])
        self.assertIsNotNone(probe_colour, "the .border probe carries no readable border colour")
        for edge, key in (
            ("topbar bottom edge", "topbarSeamColor"),
            ("bottombar top edge", "bottombarSeamColor"),
        ):
            with self.subTest(edge=edge):
                seam_colour = _normalize_colour(dark[key])
                self.assertIsNotNone(seam_colour, "%s: %r carries no readable colour" % (edge, dark[key]))
                self.assertEqual(
                    seam_colour, probe_colour,
                    "%s resolves to %s, not the current theme's border colour %s a plain core "
                    "`.border` element resolves to." % (edge, seam_colour, probe_colour),
                )

        # -- Row 3: a Chatter mounted in the (light, island) side panel stays readable -----------
        # Composited against each element's OWN real rendered background (`__effectiveBackground`)
        # - never an assumed WHITE literal, which would stay vacuously green even if the element
        # sat on a non-white background of its own.
        for label, colour_key, bg_key in (
            (".text-muted", "chatterMutedColor", "chatterMutedBg"),
        ):
            with self.subTest(chatter_surface=label):
                raw_value = dark[colour_key]
                fg_hex = _normalize_colour(raw_value)
                self.assertIsNotNone(fg_hex, "%s: %r carries no readable colour" % (label, raw_value))
                real_bg = _normalize_colour(dark[bg_key])
                self.assertIsNotNone(real_bg, "%s: %r carries no readable background" % (label, dark[bg_key]))
                composited = _composite_over(fg_hex, real_bg, _alpha_of(raw_value))
                ratio = _contrast_ratio(composited, real_bg)
                self.assertGreaterEqual(
                    round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                    "%s composites to %s on its own real background %s - only %.2f:1, below the "
                    "WCAG AA normal-text threshold %.1f:1." % (
                        label, composited, real_bg, ratio, WCAG_AA_NORMAL_TEXT,
                    ),
                )

        # -- Row 3b: the same Chatter's own follow-toggle button (a real light-island `.btn-link`)
        # stays readable in its PRESSED state too, for both schemes - the light user now also
        # mounts this Chatter (see the `light = self._measure(...)` call above), so both dicts
        # already carry `followersButton*` without a second browser session ----------------------
        for scheme_name, result in (("dark-scheme", dark), ("light-scheme", light)):
            with self.subTest(chatter_surface="follow toggle button (pressed)", scheme=scheme_name):
                bg = _normalize_colour(result["followersButtonBg"])
                self.assertIsNotNone(
                    bg, "follow toggle button: %r carries no readable background" % result["followersButtonBg"],
                )
                raw_fg = result["followersButtonActiveColor"]
                fg = _normalize_colour(raw_fg)
                self.assertIsNotNone(
                    fg, "follow toggle button (pressed): %r carries no readable colour" % raw_fg,
                )
                composited = _composite_over(fg, bg, _alpha_of(raw_fg))
                ratio = _contrast_ratio(composited, bg)
                self.assertGreaterEqual(
                    round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                    "follow toggle button (%s user), pressed: label %s on its own real "
                    "background %s measures only %.2f:1, below the WCAG AA normal-text "
                    "threshold %.1f:1." % (
                        scheme_name, composited, bg, ratio, WCAG_AA_NORMAL_TEXT,
                    ),
                )

    def test_mobile_composer_and_ribbon_menu_stay_light_islands_both_schemes(self):
        """The engine's own mobile chrome (`env.isSmall`) keeps its formula-bar composer and
        ribbon menu as light islands - readable against their own white background regardless of
        the user's colour scheme, exactly like the desktop document zone."""
        dark = self._measure_mobile(self.dark_user.login)
        light = self._measure_mobile(self.light_user.login)

        for scheme_name, result in (("dark-scheme", dark), ("light-scheme", light)):
            for surface, bg_key, fg_key in (
                (".o-small-composer (mobile formula composer)", "smallComposerBg", "smallComposerColor"),
                (".o-menu (mobile ribbon menu)", "ribbonMenuBg", "ribbonMenuItemColor"),
            ):
                with self.subTest(scheme=scheme_name, surface=surface):
                    bg = _normalize_colour(result[bg_key])
                    self.assertIsNotNone(bg, "%s: %r carries no readable background" % (surface, result[bg_key]))
                    raw_fg = result[fg_key]
                    fg = _normalize_colour(raw_fg)
                    self.assertIsNotNone(fg, "%s label: %r carries no readable colour" % (surface, raw_fg))
                    composited = _composite_over(fg, bg, _alpha_of(raw_fg))
                    ratio = _contrast_ratio(composited, bg)
                    self.assertGreaterEqual(
                        round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                        "%s (%s user): label %s on its own real background %s measures only "
                        "%.2f:1, below the WCAG AA normal-text threshold %.1f:1 - a light island "
                        "must stay readable against its OWN background, not the dark chrome's." % (
                            surface, scheme_name, composited, bg, ratio, WCAG_AA_NORMAL_TEXT,
                        ),
                    )

    def test_mobile_dark_scheme_sheds_core_light_topbar_glow_and_bottombar_menu_border(self):
        """A dark-scheme user on the mobile viewport (`env.isSmall`) loses core's own light
        seams too - the topbar-wrapper's glow shadow and the bottombar's menu-row border -
        exactly like the desktop chrome already sheds its own analogous seams for this user."""
        dark = self._measure_mobile(self.dark_user.login)

        self.assertEqual(
            dark["topbarWrapperBoxShadow"], "none",
            "the mobile topbar-wrapper still renders core's own light glow box-shadow (%r) for "
            "a dark-scheme user - it must resolve to 'none', exactly like the "
            "bottombar-wrapper's own existing box-shadow: none treatment." % dark["topbarWrapperBoxShadow"],
        )

        probe_colour = _normalize_colour(dark["probeBorderColor"])
        self.assertIsNotNone(probe_colour, "the .border probe carries no readable border colour")
        menu_border_colour = _normalize_colour(dark["bottomBarMenuBorderColor"])
        self.assertIsNotNone(
            menu_border_colour,
            "mobile bottom-bar-menu: %r carries no readable border colour" % dark["bottomBarMenuBorderColor"],
        )
        self.assertEqual(
            menu_border_colour, probe_colour,
            "the mobile bottom-bar-menu's border resolves to %s, not the current theme's border "
            "colour %s a plain core `.border` element resolves to." % (menu_border_colour, probe_colour),
        )

    def test_pressed_link_style_button_outside_light_island_stays_core_governed(self):
        """A `.btn-link` outside every light island - the irregularity map's own "Turn off"
        button, rendered by the engine directly on the dark topbar chrome, never inside
        `.o-sidePanel`/`.o-popover` - keeps whatever PRESSED-state ink the untouched cascade
        leaves it: this module's own pressed-state lever is scoped to light islands only and
        must not reach a surface outside that scope. This test makes no readability claim for
        that ink - this surface's own contrast is governed upstream of this module's lever, so
        certifying it is not this test's job."""
        dark = self._measure(
            self.dark_user.login, "viin-chrome-dark-irregularity-test-carousel",
            chatter_js=_IRREGULARITY_MAP_JS,
        )

        raw_fg = dark["irregularityTurnOffActiveColor"]
        fg = _normalize_colour(raw_fg)
        self.assertIsNotNone(
            fg, "irregularity map Turn off button (pressed): %r carries no readable colour" % raw_fg,
        )
        core_os_text_body = _core_os_text_body()
        self.assertIsNotNone(
            core_os_text_body,
            "%s must assign a hex to $os-text-body (directly or via a $var), so this test can "
            "compare against the live SSOT instead of a hardcoded literal." % CORE_SPREADSHEET_VARIABLES_SCSS,
        )
        self.assertNotEqual(
            fg, core_os_text_body,
            "irregularity map Turn off button (pressed): reads %s ($os-text-body, this "
            "module's light-island pressed-state override) - the irregularity map sits directly "
            "on the dark topbar chrome, not a light island, so this module's light-island-only "
            "lever must not reach it." % core_os_text_body,
        )
