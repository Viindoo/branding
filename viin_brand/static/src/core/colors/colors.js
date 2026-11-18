/** @odoo-module **/

/* eslint-disable no-import-assign */
// Viindoo graph/pivot/dashboard palette override.
//
// Core builds chart series colours from module-private palettes and exposes them only through the
// exported getColor()/getColors(), with no registry entry, CSS variable or arch option. The
// transpiler compiles `export function getColor` to a writable `__exports.getColor`, so
// reassigning it here retints every consumer that reads the export after this file runs.
//
// The file is eager (a bare entry in web.assets_backend): a consumer's
// `import { getColor } from "@web/core/colors/colors"` compiles to a destructuring snapshot taken
// when that consumer's factory runs. The graph, pivot and dashboard views are lazy, so they
// snapshot the patched getColor.
//
// Both exports are closures over the brand arrays below: core's getColor calls its module-local
// getColors binding, so patching getColors alone would be inert.
//
// Known gap: the accounting journal-card sparkline (journal_dashboard_graph_field.js) is an eager
// field widget whose factory runs before this module, so it keeps core's colours.
import * as colors from "@web/core/colors/colors";

// LIGHT scheme (readable on the default light backend). Teal first, then spread so the first six
// (the sm palette, used by most small charts) are maximally hue-separated.
const BRAND_COLORS_LIGHT = [
    "#00BBCE", // Teal - brand primary ($o-brand-primary)
    "#CC5252", // Red - danger ($o-danger)
    "#00B365", // Green - success ($o-success)
    "#FFA100", // Orange
    "#7F4282", // Purple - brand secondary ($o-brand-secondary)
    "#0099E6", // Blue - info ($o-info)
    "#FFCC32", // Yellow - warning ($o-warning)
    "#DD3BAF", // Magenta
    "#804080", // Deep purple
    "#343A40", // Charcoal
];

// DARK scheme (readable on the dark backend): lighter variants in the same hue order as
// BRAND_COLORS_LIGHT, so a series index keeps its hue across schemes.
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
    "#929CA6", // Grey (for #343A40)
];

// sm palette (<= 6 series): the six most hue-separated brand colours, teal first.
const BRAND_SM_LIGHT = BRAND_COLORS_LIGHT.slice(0, 6);
const BRAND_SM_DARK = BRAND_COLORS_DARK.slice(0, 6);

// The named "odoo" palette: core ships an aubergine trio; a caller passing the literal "odoo"
// palette name gets a teal-family trio instead.
const BRAND_ODOO_LIGHT = ["#00BBCE", "#007F8E", "#66F0FF"]; // teal, AA dark teal, light teal
const BRAND_ODOO_DARK = ["#66F0FF", "#00BBCE", "#C796CA"]; // light teal, teal, light purple

/**
 * Brand replacement for core getColors: returns the branded array for a colour scheme and a
 * resolved palette name. md/lg/xl reuse the full ten-hue array, wrapping via the index modulo in
 * getColor.
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
 * Brand replacement for core getColor. Mirrors core's size/name resolution (sm <= 6 / md <= 12 /
 * lg <= 24 / xl, the named "odoo" palette, dark-scheme variants); only the palette values change.
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

// getColors is reassigned too so direct getColors consumers are retinted; the renderers call
// getColor.
colors.getColors = brandGetColors;
colors.getColor = brandGetColor;
