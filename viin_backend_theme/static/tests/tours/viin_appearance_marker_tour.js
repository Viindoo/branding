// Guards: with the Appearance systray open, the row for the currently selected option renders
// exactly one visible selected-marker, in both colour schemes. Driven by tests/test_tours.py.
//
// Core paints its own ::before checkmark on any `.dropdown-item.active` unless the item carries the
// opt-out class `dropdown-item_active_noarrow` (web/static/src/webclient/webclient.scss); this
// component also renders its own check icon, so without the opt-out both paint. The assertion
// reads the rendered result (the computed `::before` content and the visible check icons), not a
// class string.

import { registry } from "@web/core/registry";

const tours = registry.category("web_tour.tours");

// Every currently-active option row (Theme's current pick, Density's current pick) must show
// exactly one visible marker, with core's own ::before glyph suppressed on all of them.
function assertEveryActiveOptionShowsExactlyOneMarker() {
    const activeRows = document.querySelectorAll(".o_viin_appearance_option.active");
    if (activeRows.length === 0) {
        throw new Error("expected at least one active appearance option row, found none");
    }
    for (const row of activeRows) {
        const beforeContent = window.getComputedStyle(row, "::before").content;
        if (beforeContent !== "none") {
            throw new Error(
                "active row's own ::before must compute to 'none' (core's marker must not " +
                    `paint on top of the component's own check), found ${beforeContent}`
            );
        }
        const visibleChecks = [...row.querySelectorAll(".oi[data-icon='check']")].filter((icon) => {
            const style = window.getComputedStyle(icon);
            return style.display !== "none" && style.visibility !== "hidden";
        });
        if (visibleChecks.length !== 1) {
            throw new Error(
                "active row must render exactly ONE visible selected-marker, found " +
                    `${visibleChecks.length}`
            );
        }
    }
}

tours.add("viin_appearance_marker_count_light_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "open the appearance systray",
            trigger: ".o_viin_appearance_toggle",
            run: "click",
        },
        {
            content:
                "in the default LIGHT scheme, every active option row shows exactly one marker",
            trigger: ".o_viin_appearance_option.active",
            run: assertEveryActiveOptionShowsExactlyOneMarker,
        },
    ],
});

// Choosing Dark persists the preference and reloads (there is no in-place flip), so the menu is
// re-opened after the reload.
tours.add("viin_appearance_marker_count_dark_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "open the appearance systray",
            trigger: ".o_viin_appearance_toggle",
            run: "click",
        },
        {
            content: "choose the Dark scheme - persists the pref + cookie and reloads",
            trigger: ".o_viin_appearance_option:contains(Dark)",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "after the reload the server serves the dark bundle",
            trigger: "html[data-bs-theme='dark']",
        },
        {
            content: "re-open the appearance systray under the dark scheme",
            trigger: ".o_viin_appearance_toggle",
            run: "click",
        },
        {
            content: "in the DARK scheme too, every active option row shows exactly one marker",
            trigger: ".o_viin_appearance_option.active",
            run: assertEveryActiveOptionShowsExactlyOneMarker,
        },
    ],
});
