import { describe, expect, test } from "@odoo/hoot";

// The backend graph / pivot / dashboard charts must render the Viindoo brand palette (purple
// first, cyan second), never core's blue-first palette. Core exposes chart series colours only
// through getColor() in web/static/src/core/colors/colors.js. viin_brand reassigns that export
// eagerly in static/src/core/colors/colors.js; importing the override as a side effect runs the
// reassignment before any test body executes.
//
// The tests protect the three getColor capabilities: (1) size-keyed palettes, (2) the named
// "odoo" branch, (3) dark-scheme variants.
import { getColor } from "@web/core/colors/colors";
import "@viin_brand/core/colors/colors";

describe.current.tags("headless");

const HEX = /^#[0-9A-Fa-f]{6}$/;

test("graph series 1 and 2 are the Viindoo purple and cyan, not core blue", () => {
    // paletteSizeOrName = 1 resolves the sm tier; unpatched core returns COLORS_SM[0] = "#4EA7F2".
    expect(getColor(0, "light", 1)).toBe("#7F4282");
    expect(getColor(1, "light", 1)).toBe("#00BBCE");
});

test("a multi-series chart keeps at least 6 distinct brand colours (legibility floor)", () => {
    // capability 1: a 12-dataset call resolves the md tier; it must stay legible with >= 6
    // distinct hues, and the brand purple must still lead the series.
    const swatches = Array.from({ length: 12 }, (_, index) => getColor(index, "light", 12));
    expect(new Set(swatches).size).toBeGreaterThan(5); // strictly > 5, i.e. >= 6 distinct
    expect(swatches[0]).toBe("#7F4282");
});

test('the "odoo" named-palette branch is preserved and brand-purple-first', () => {
    // capability 2: the explicit "odoo" palette-name branch must still resolve to valid brand
    // colours (core routes the accounting sparkline through it).
    expect(getColor(0, "light", "odoo")).toBe("#7F4282");
    expect(getColor(1, "light", "odoo")).toBe("#00BBCE");
    expect(getColor(2, "light", "odoo")).toMatch(HEX);
});

test("dark-scheme variants are preserved and honour the colour scheme", () => {
    // capability 3: a dark colorScheme call returns the lighter variants of the same hue order,
    // proving colorScheme is honoured, not ignored.
    expect(getColor(0, "dark", 1)).toBe("#C796CA");
    expect(getColor(1, "dark", 1)).toBe("#66F0FF");
    expect(getColor(0, "dark", 1)).not.toBe(getColor(0, "light", 1));
    expect(getColor(0, "dark", "odoo")).toBe("#C796CA");
});
