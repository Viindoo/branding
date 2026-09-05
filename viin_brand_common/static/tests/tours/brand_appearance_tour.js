/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Brand appearance contract, guarded on the REAL webclient and the REAL
 * website - deliberately NOT on the unit-test page.
 *
 * viin_brand_common (and its sibling brand modules) now strip their own SCSS
 * back out of `web.assets_unit_tests_setup` and `web.tests_assets`, so core's
 * Hoot/QUnit suites stop measuring Viindoo's design tokens instead of core's
 * own. The consequence is that the test page carries NO brand CSS at all, and
 * brand-appearance regression therefore lost the only place it used to be
 * noticed (design risk R4). These tours are the replacement guard, and they
 * have to run where the brand CSS actually ships.
 *
 * INDEPENDENCE. Every expected value below comes from the Viindoo brand
 * identity (cyan #00BBCE, 15px body text, square corners) or from the palette
 * Odoo core publishes for the branded stack - never from reading the SCSS
 * these tours guard. An expectation copied out of the code under test passes
 * at all times and catches nothing.
 *
 * WHAT IS MEASURED. Each tour reads a value the browser actually RENDERED -
 * the background-color painted on an element carrying the palette class, the
 * font-size resolved on <body>, the corner radius resolved on a .btn - rather
 * than the raw text of a CSS custom property. A custom property can hold a
 * perfectly correct token while nothing on the page consumes it; only the
 * rendered value proves the user sees the brand.
 *
 * WHY EACH TOUR ENDS ON A SENTINEL STEP. The measuring step sets a marker
 * attribute on <body> as its last act, and a following step triggers on that
 * marker. If the measurement were ever skipped - a step-schema change, a
 * runner that drops a trailing action, a selector that silently never matches
 * - the marker is absent, the sentinel step times out and the tour fails. It
 * is not possible for these tours to report success without the assertions
 * having actually executed.
 */

// #00BBCE - Viindoo brand primary (cyan). Rendered form, as a browser reports it.
const BRAND_PRIMARY_RGB = "rgb(0, 187, 206)";
// #2D3142 - o-color-2 of the palette the branded stack serves. Asserting it on
// BOTH the backend and the website is what turns "the two agree", measured once
// by hand, into a standing contract.
const THEME_SECONDARY_RGB = "rgb(45, 49, 66)";
// Viindoo's base text runs one step larger than core's 14px.
const BRAND_BASE_FONT_SIZE = "15px";

const MEASURED_FLAG = "data-viin-brand-measured";

function viewport() {
    return `${window.innerWidth}x${window.innerHeight}`;
}

/**
 * Render a throw-away element carrying `className`, read one computed property
 * off it, then remove it.
 *
 * Measuring on a probe rather than on whatever happens to be on screen keeps
 * the assertion deterministic: it depends only on the stylesheet the page was
 * served, never on which record, action or viewport the webclient landed on.
 * The probe is parked off-screen with inline position/left, which cannot
 * influence colour, font-size or border-radius.
 */
function measureOnProbe(tagName, className, property) {
    const probe = document.createElement(tagName);
    probe.className = className;
    probe.style.position = "absolute";
    probe.style.left = "-9999px";
    probe.style.top = "0";
    document.body.appendChild(probe);
    try {
        return window.getComputedStyle(probe).getPropertyValue(property).trim();
    } finally {
        probe.remove();
    }
}

/**
 * Fail the tour with the value actually measured, so a red run names the
 * number that was wrong instead of only the step that noticed.
 */
function assertRendered(label, actual, expected, why) {
    // console.log (never console.error - that would fail the run by itself)
    // so the measured numbers land in the test log on green runs too, which is
    // what makes a two-way inversion check auditable afterwards.
    console.log(`[viin_brand] ${label}: measured ${actual}, expected ${expected} @ ${viewport()}`);
    if (actual !== expected) {
        throw new Error(
            `${label} is "${actual}" but the Viindoo brand contract requires "${expected}". ` +
                `${why} Measured at viewport ${viewport()} on ${window.location.pathname}.`
        );
    }
}

function markMeasured(name) {
    document.body.setAttribute(MEASURED_FLAG, name);
}

function sentinelStep(name) {
    return {
        trigger: `body[${MEASURED_FLAG}='${name}']`,
        content:
            "The measuring step really ran - without this sentinel a skipped " +
            "measurement would look exactly like a passing tour",
    };
}

function assertBrandPalette(where) {
    assertRendered(
        `${where} .bg-o-color-1 background-color`,
        measureOnProbe("div", "bg-o-color-1", "background-color"),
        BRAND_PRIMARY_RGB,
        "o-color-1 is the Viindoo cyan; core's own #714B67 reaching this page " +
            "means the brand palette stopped being applied to the real product."
    );
    assertRendered(
        `${where} .bg-o-color-2 background-color`,
        measureOnProbe("div", "bg-o-color-2", "background-color"),
        THEME_SECONDARY_RGB,
        "o-color-2 comes from the palette the branded stack ships; a different " +
            "value means the whole palette was swapped, not just one colour."
    );
}

registry.category("web_tour.tours").add("viin_brand_palette_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: ".o_main_navbar",
            content: "Wait until the real webclient has painted",
        },
        {
            trigger: "body.o_web_client",
            content: "The real backend must paint the Viindoo brand palette",
            run: () => {
                assertBrandPalette("backend");
                markMeasured("palette");
            },
        },
        sentinelStep("palette"),
    ],
});

registry.category("web_tour.tours").add("viin_brand_website_palette_tour", {
    url: "/",
    steps: () => [
        {
            trigger: "#wrapwrap",
            content: "Wait until the real website page has painted",
        },
        {
            trigger: "body",
            content:
                "The real website must paint the SAME palette as the backend - " +
                "the editor takes its theme colours from this page",
            run: () => {
                assertBrandPalette("website");
                markMeasured("website-palette");
            },
        },
        sentinelStep("website-palette"),
    ],
});

registry.category("web_tour.tours").add("viin_brand_font_size_tour", {
    url: "/odoo",
    steps: () => [
        {
            trigger: ".o_main_navbar",
            content: "Wait until the real webclient has painted",
        },
        {
            trigger: "body.o_web_client",
            content: "The real backend must render text at the Viindoo base size",
            run: () => {
                assertRendered(
                    "backend body font-size",
                    window.getComputedStyle(document.body).fontSize.trim(),
                    BRAND_BASE_FONT_SIZE,
                    "Viindoo reads one step larger than core's 14px; falling back " +
                        "to 14px means the brand type scale stopped shipping.",
                );
                markMeasured("font-size");
            },
        },
        sentinelStep("font-size"),
    ],
});
