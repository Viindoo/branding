/** @odoo-module **/

/* eslint-disable no-import-assign */
// ---------------------------------------------------------------------------------------------
// Viindoo graph/pivot/dashboard palette override (v19 3-arg port of the 18.0 GRAPH_COLORS layer).
//
// WHY an export monkeypatch and not a registry/patch()/CSS-var hook: core builds chart series
// colours from module-PRIVATE palette consts in web/static/src/core/colors/colors.js and exposes
// them ONLY through the exported getColor()/getColors(). There is no registry entry, no CSS
// variable and no arch option to retint them (verified against 19.0 core). The one supported seam
// is to reassign the writable export: Odoo's JS transpiler compiles `export function getColor` to
// `__exports.getColor = getColor` (a plain writable data property), so overwriting
// `colors.getColor` here is honoured by every consumer that reads the export AFTER this file runs.
//
// WHY this file must be EAGER (a bare side-effect entry in web.assets_backend): the transpiler
// compiles a consumer's `import { getColor } from "@web/core/colors/colors"` to a destructuring
// SNAPSHOT `const { getColor } = require(...)` taken when that consumer module's factory runs.
// The graph renderer, pivot and dashboard views are LAZY (their factories run only when the view
// is opened - always after boot), while this module loads eagerly at def-index ~1257, so those
// lazy consumers snapshot the PATCHED getColor. See tests/test_asset_upgrade.py for the wiring
// guard and static/tests/colors_debrand.test.js for the behaviour guard.
//
// WHY getColor is fully self-contained (not delegating to the core export): core's own getColor
// calls its module-LOCAL `getColors` binding, which is unreachable from outside - patching the
// getColors export alone is therefore inert. Both exports below are reassigned to closures that
// read ONLY the brand arrays in this file, so the retint holds even if another layer later
// re-patches getColors.
//
// KNOWN CAVEAT (documented, deliberately NOT fixed here): the Accounting journal-card sparkline
// (web/static/src/views/fields/journal_dashboard_graph/journal_dashboard_graph_field.js) is an
// EAGER field widget registered at boot. Its factory runs BEFORE this module (lower def-index),
// so it snapshots core's ORIGINAL getColor and keeps core's blue-first "odoo" trio. Retinting it
// too would need a separate component patch() of JournalDashboardGraphField - left for a human
// decision (see the agent report).
//
// PALETTE PROVENANCE: hues are the approved 18.0 brand graph palette
// (origin/18.0 viin_brand_common/static/src/core/colors/colors.js GRAPH_COLORS, dropped in the
// v19 upgrade commit 3c9120e) reconciled with the brand SSOT
// (static/src/scss/brand_variables.scss). No off-brand hue is invented: the sets below are the
// 18.0 saturated series and its paired lighter series, reordered teal-first for maximal
// small-chart distinctness, with the 18.0 typo "929ca6" corrected to "#929CA6".
// ---------------------------------------------------------------------------------------------
import * as colors from "@web/core/colors/colors";

// LIGHT scheme (readable on the default light backend): the 18.0 saturated brand series.
// Order = teal-first then spread so the first six (the sm palette / most common small charts)
// are maximally hue-separated. Index 0 is the Viindoo brand teal.
const BRAND_COLORS_LIGHT = [
    "#00BBCE", // Teal - brand primary ($o-brand-primary)
    "#CC5252", // Red - danger ($o-danger)
    "#00B365", // Green - success ($o-success)
    "#FFA100", // Orange (18.0 series)
    "#7F4282", // Purple - brand secondary ($o-brand-secondary)
    "#0099E6", // Blue - info ($o-info)
    "#FFCC32", // Yellow - warning ($o-warning)
    "#DD3BAF", // Magenta (18.0 series)
    "#804080", // Deep purple (18.0 series)
    "#343A40", // Charcoal (18.0 series)
];

// DARK scheme (readable on the dark backend): the 18.0 paired lighter series, same hue order as
// BRAND_COLORS_LIGHT so a given series index keeps its hue identity across schemes. Index 0 is a
// light teal (the brand-teal family) - teal-first is preserved in dark mode too.
const BRAND_COLORS_DARK = [
    "#66F0FF", // Light teal (for #00BBCE)
    "#E5A8A8", // Light red (for #CC5252)
    "#59FFB6", // Light green (for #00B365)
    "#FFD07F", // Light orange (for #FFA100)
    "#C796CA", // Light purple (for #7F4282)
    "#73D0FF", // Light blue (for #0099E6)
    "#FFE598", // Light yellow (for #FFCC32)
    "#EE9DD6", // Light magenta (for #DD3BAF)
    "#CA95CA", // Light deep purple (for #804080)
    "#929CA6", // Grey (for #343A40; 18.0 typo "929ca6" corrected)
];

// sm palette (<= 6 series): the six most hue-separated brand colours, teal first.
const BRAND_SM_LIGHT = BRAND_COLORS_LIGHT.slice(0, 6);
const BRAND_SM_DARK = BRAND_COLORS_DARK.slice(0, 6);

// The named "odoo" palette (capability 2): core ships a 3-colour brand trio here (aubergine
// family). Rebuilt as a teal-family trio, teal first, per scheme. Any caller passing the literal
// "odoo" palette name (e.g. a lazy consumer) gets brand teal instead of core aubergine.
const BRAND_ODOO_LIGHT = ["#00BBCE", "#007F8E", "#66F0FF"]; // teal, AA dark teal, light teal
const BRAND_ODOO_DARK = ["#66F0FF", "#00BBCE", "#C796CA"]; // light teal, teal, light purple

/**
 * Brand replacement for core getColors: returns the branded array for a colour scheme and a
 * resolved palette name. md/lg/xl reuse the full ten-hue master array (>= 6 distinct, wrapping via
 * the index modulo in getColor) - the "reuse/repeat sensibly" tier fill, keeping every entry a
 * literal brand hue rather than an invented shade ladder.
 *
 * @param {string} colorScheme "dark" selects the lighter dark-scheme variants; anything else the
 *   light-scheme variants.
 * @param {string} paletteName one of "odoo" | "sm" | "md" | "lg" | (default) "xl".
 * @returns {string[]}
 */
function brandGetColors(colorScheme, paletteName) {
    const dark = colorScheme === "dark";
    switch (paletteName) {
        case "odoo":
            return dark ? BRAND_ODOO_DARK : BRAND_ODOO_LIGHT;
        case "sm":
            return dark ? BRAND_SM_DARK : BRAND_SM_LIGHT;
        case "md":
        case "lg":
        default:
            return dark ? BRAND_COLORS_DARK : BRAND_COLORS_LIGHT;
    }
}

/**
 * Brand replacement for core getColor. Mirrors core's exact size/name resolution ladder so all
 * three v19 capabilities are preserved: (1) size-keyed palettes (sm <= 6 / md <= 12 / lg <= 24 /
 * xl), (2) the named "odoo" branch, (3) dark-scheme variants. Only the palette VALUES change.
 * Self-contained: reads brandGetColors (a local binding), never the core export.
 *
 * @param {number} index series index (wrapped modulo palette length).
 * @param {string} colorScheme "dark" | anything else.
 * @param {number|string} paletteSizeOrName dataset count, or an explicit palette name.
 * @returns {string} a "#RRGGBB" colour.
 */
function brandGetColor(index, colorScheme, paletteSizeOrName) {
    let paletteName;
    if (paletteSizeOrName === "odoo") {
        paletteName = "odoo";
    } else if (paletteSizeOrName <= 6 || paletteSizeOrName === "sm") {
        paletteName = "sm";
    } else if (paletteSizeOrName <= 12 || paletteSizeOrName === "md") {
        paletteName = "md";
    } else if (paletteSizeOrName <= 24 || paletteSizeOrName === "lg") {
        paletteName = "lg";
    } else {
        paletteName = "xl";
    }
    const palette = brandGetColors(colorScheme, paletteName);
    return palette[index % palette.length];
}

// Reassign both writable exports. getColors is mirrored so any direct getColors consumer is also
// retinted; getColor is what the graph/pivot/dashboard renderers actually call.
colors.getColors = brandGetColors;
colors.getColor = brandGetColor;
