# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import json

from odoo.tests import HttpCase, new_test_user, tagged
from odoo.tools.misc import file_open

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    WCAG_NON_TEXT_MIN,
    _alpha_of,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    _relative_luminance,
)
from odoo.addons.viin_brand.tests.test_brand_ssot import _resolve_scss_hex

# Registry tag the test-only client action registers under
# (static/tests/tours/test_spreadsheet_editor_action.js).
TEST_EDITOR_ACTION_TAG = "viin_brand_spreadsheet_chrome_dark_test_editor"

# Upper bound of "reads as a dark surface" (Viindoo's dark tokens sit near 0.0, CE's light chrome
# near 1.0). A surface is dark only if this holds AND it differs from the light-scheme user's.
DARK_CHROME_MAX_RELATIVE_LUMINANCE = 0.4

# $os-text-body is resolved from core's SCSS rather than copied, so a core re-tune keeps the
# assertions correct.
CORE_SPREADSHEET_VARIABLES_SCSS = "spreadsheet/static/src/o_spreadsheet/o_spreadsheet_variables.scss"

_core_os_text_body_cache = {}


def _core_os_text_body():
    """Return the hex ``$os-text-body`` resolves to in core's spreadsheet SCSS.

    :return: the normalised colour, or ``None`` when the variable cannot be found
    """
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


# One browser session mounts the editor and measures the chrome, a carousel figure with its side
# panel, the filter-menu popover, the optional extra snippet (a Chatter or the irregularity map)
# and the grid/chrome seam against a live `.border` probe. Only core classes and core stores are
# queried, never a business-module selector.
# The engine's injected `.o-hoverable-button .o-icon` rule applies only to the topbar (the bottombar
# renders no such button), and its `.o-topbar-composer` is a forced-white light island that must
# not inherit the chrome's dark text colour.
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
// A topbar button another module contributes: a font-glyph icon with no colour of its own.
const __glyphButton = document.createElement("button");
__glyphButton.className = "o-hoverable-button border-0 bg-transparent rounded px-1 py-2";
__glyphButton.innerHTML = '<i class="fa fa-filter"></i>';
__topbarWrapper.appendChild(__glyphButton);
const __glyphIcon = __glyphButton.querySelector("i");
const __fontSizeInput = await __waitFor(() => __topbarWrapper.querySelector("input.o-font-size"), 15000);
const __sheetIcon = await __waitFor(
    () => __bottombarWrapper.querySelector(".o-sheet.active .o-sheet-icon"), 15000
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
    glyphIconColor: getComputedStyle(__glyphIcon).color,
    fontSizeInputColor: getComputedStyle(__fontSizeInput).color,
    fontSizeInputBg: __effectiveBackground(__fontSizeInput),
    sheetIconColor: getComputedStyle(__sheetIcon).color,
    sheetIconBg: __effectiveBackground(__sheetIcon),
    topbarComposerBg: __effectiveBackground(__topbarComposerInput),
    topbarComposerColor: getComputedStyle(__topbarComposerInput).color,
};

%(chatter_js)s

await __setParam(%(param_key)r, JSON.stringify(__result));
"""

# Mounts a core Chatter on a test partner inside the side panel and measures its muted text
# against its own real rendered background, plus the follow button's pressed ink, read through
# `--btn-active-color` because a script cannot force `:active`.
_CHATTER_JS = """
const __probe = document.createElement("div");
__probe.className = "border";
__probe.style.position = "absolute";
__probe.style.visibility = "hidden";
document.body.appendChild(__probe);
__result.probeBorderColor = getComputedStyle(__probe).borderTopColor;

const __owl = odoo.loader.modules.get("@odoo/owl");
const __chatterModule = odoo.loader.modules.get("@mail/chatter/web_portal/chatter");
// A standalone App needs the `getTemplate` option to resolve the named "mail.Chatter" template.
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

# Opens "View > Irregularity map" by real clicks. That panel renders on the dark topbar chrome,
# outside every light island; its "Turn off" `.btn-link` pressed ink is read through
# `--btn-active-color`. Runs through the `chatter_js` slot of `_measure()`.
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

# Mounts the editor on a narrow viewport so the engine's own `isSmall` breakpoint swaps in the
# mobile composer and ribbon menu. `.bottom-bar-menu` and the topbar glow are read before the
# ribbon click, which removes that menu from the DOM.
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
    """The editor's command chrome follows a dark-scheme user; its document zone stays light.

    The grid, side panel, chart-figure header and filter-menu popover render identically for both
    schemes, the formula-bar composer and the mobile composer and ribbon menu are light islands
    readable on their own background, and a Chatter in the side panel stays readable.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `base.group_system` is needed only by the measurement relay, which stores results through
        # `ir.config_parameter.set_param`.
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
            "the browser measurement under login %r reported no value - the test editor action "
            "did not mount." % login,
        )
        return json.loads(raw)

    def _measure_mobile(self, login):
        param_key = "viin_brand_spreadsheet.chrome_dark_mobile_test.%s" % login
        code = _wrap(_MEASURE_MOBILE_JS % {
            "action_tag": TEST_EDITOR_ACTION_TAG,
            "param_key": param_key,
        })
        # `browser_size` is read when each `browser_js()` starts; narrowing it flips the engine's
        # own mobile breakpoint.
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
            "the mobile measurement under login %r reported no value - `.o-small-composer` did "
            "not mount at the narrow viewport." % login,
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

        # The chrome repaints dark with every label readable on it.
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
                self.assertIsNotNone(
                    label_colour, "%s label: %r carries no readable colour" % (surface, dark[label_key]),
                )
                ratio = _contrast_ratio(label_colour, dark_bg)
                self.assertGreaterEqual(
                    round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                    "%s label %s on its own dark background %s measures only %.2f:1, below the "
                    "WCAG AA normal-text threshold %.1f:1." % (
                        surface, label_colour, dark_bg, ratio, WCAG_AA_NORMAL_TEXT,
                    ),
                )

        # The toolbar icon reads against the topbar's dark background.
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

        # A glyph icon another module adds, the font-size field and the active sheet tab's caret
        # read against the fill they are painted on.
        for surface, colour_key, bg_key, floor in (
            ("topbar glyph icon", "glyphIconColor", "topbarBg", WCAG_NON_TEXT_MIN),
            ("font-size field", "fontSizeInputColor", "fontSizeInputBg", WCAG_AA_NORMAL_TEXT),
            ("active sheet tab icon", "sheetIconColor", "sheetIconBg", WCAG_NON_TEXT_MIN),
        ):
            with self.subTest(surface=surface):
                fg = _normalize_colour(dark[colour_key])
                bg = _normalize_colour(dark[bg_key])
                self.assertIsNotNone(fg, "%s: %r carries no readable colour" % (surface, dark[colour_key]))
                self.assertIsNotNone(bg, "%s: %r carries no readable colour" % (surface, dark[bg_key]))
                ratio = _contrast_ratio(fg, bg)
                self.assertGreaterEqual(
                    round(ratio, 2), floor,
                    "%s %s on its dark chrome background %s measures only %.2f:1, below %.1f:1."
                    % (surface, fg, bg, ratio, floor),
                )

        # The formula-bar composer is a light island: readable on its own background.
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

        # A light-scheme user's label keeps the engine's stock colour.
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

        # The document zone is identical between the two schemes.
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

        # The grid/chrome seam equals a live core `.border` probe.
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

        # A Chatter in the light-island side panel stays readable, composited against each element's
        # own rendered background rather than an assumed white.
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

        # The follow-toggle `.btn-link` stays readable when pressed, for both schemes.
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
        """The mobile formula composer and ribbon menu stay light islands for both colour schemes."""
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
        """On the mobile viewport a dark-scheme user loses core's light topbar glow and bottom-bar menu border."""
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
        """The pressed-state ink override stays scoped to light islands.

        The irregularity map's "Turn off" ``.btn-link`` sits on the dark topbar chrome, outside
        ``.o-sidePanel`` and ``.o-popover``, so its pressed ink must not be the island override.
        No readability claim is made for that surface.
        """
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
