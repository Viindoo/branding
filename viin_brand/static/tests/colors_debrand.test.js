import { describe, expect, test } from "@odoo/hoot";

// The backend graph / pivot / dashboard charts must render the Viindoo brand palette (teal-first),
// never core's blue-first palette. Core exposes chart series colours only through getColor() in
// web/static/src/core/colors/colors.js, whose unpatched sm-palette leads with "#4EA7F2" (blue).
// viin_brand reassigns that export eagerly in static/src/core/colors/colors.js; importing the
// override as a side effect runs the reassignment before any test body executes.
//
// The following tests protect the three getColor capabilities of 19.0: (1) size-keyed palettes,
// (2) the named "odoo" branch, (3) dark-scheme variants.
import { getColor } from "@web/core/colors/colors";
import "@viin_brand/core/colors/colors";

describe.current.tags("headless");

const HEX = /^#[0-9A-Fa-f]{6}$/;

test("graph series index 0 is the Viindoo brand teal, not core blue", () => {
    // paletteSizeOrName = 1 resolves the sm tier; index 0 must be the brand teal, where unpatched
    // core returns COLORS_SM[0] = "#4EA7F2" (blue).
    expect(getColor(0, "light", 1)).toBe("#00BBCE");
});

test("a multi-series chart keeps at least 6 distinct brand colours (legibility floor)", () => {
    // capability 1: a 12-dataset call resolves the md tier; it must stay legible with >= 6
    // distinct hues, and the brand teal must still lead the series.
    const swatches = Array.from({ length: 12 }, (_, index) => getColor(index, "light", 12));
    expect(new Set(swatches).size).toBeGreaterThan(5); // strictly > 5, i.e. >= 6 distinct
    expect(swatches[0]).toBe("#00BBCE");
});

test('the "odoo" named-palette branch is preserved and brand-teal-first', () => {
    // capability 2: the explicit "odoo" palette-name branch must still resolve to valid brand
    // colours (core routes the accounting sparkline through it).
    expect(getColor(0, "light", "odoo")).toBe("#00BBCE");
    expect(getColor(1, "light", "odoo")).toMatch(HEX);
    expect(getColor(2, "light", "odoo")).toMatch(HEX);
});

test("dark-scheme variants are preserved and honour the colour scheme", () => {
    // capability 3: a dark colorScheme call still returns a valid colour, and the dark teal
    // differs from the light teal - proving colorScheme is honoured, not ignored.
    const darkTeal = getColor(0, "dark", 1);
    expect(darkTeal).toMatch(HEX);
    expect(darkTeal).toBe("#66F0FF");
    expect(darkTeal).not.toBe(getColor(0, "light", 1));
});
