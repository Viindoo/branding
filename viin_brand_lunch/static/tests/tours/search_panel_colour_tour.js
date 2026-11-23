// Guards: no section icon of the search panel of the lunch products carries a colour of Odoo, and
// the icon of the categories takes the colour of a link of the palette, in both colour schemes.
// The assertions read the browser's own computed style. Driven by tests/test_search_panel_colour.py.

import { registry } from "@web/core/registry";

// The palette of Odoo that the icons must not carry: the data of the assertion, never painted.
const ODOO_COLOURS = ["#875A7B", "#714B67", "#71639E", "#017E84", "#00A09D", "#008384"];

function resolveColour(colour) {
    const probe = document.createElement("span");
    probe.style.color = colour;
    document.body.appendChild(probe);
    const resolved = getComputedStyle(probe).color;
    probe.remove();
    return resolved;
}

function linkColour() {
    const probe = document.createElement("a");
    probe.href = "#";
    document.body.appendChild(probe);
    const resolved = getComputedStyle(probe).color;
    probe.remove();
    return resolved;
}

function assertSectionIconsFollowThePalette(scheme) {
    const theme = document.documentElement.getAttribute("data-bs-theme");
    if (theme !== scheme) {
        throw new Error(`expected the ${scheme} scheme to be served, found data-bs-theme=${theme}`);
    }
    const icons = [...document.querySelectorAll(".o_search_panel_section_icon")];
    if (icons.length < 2) {
        throw new Error(`expected the Categories and the Vendors icons, found ${icons.length}`);
    }
    const odoo = ODOO_COLOURS.map(resolveColour);
    for (const icon of icons) {
        const colour = getComputedStyle(icon).color;
        if (odoo.includes(colour)) {
            throw new Error(`a section icon carries the colour of Odoo: ${colour}`);
        }
    }
    const categories = document.querySelector(
        ".o_search_panel_section_icon[data-icon='restaurant']"
    );
    if (!categories) {
        throw new Error("the icon of the Categories section is missing");
    }
    if (getComputedStyle(categories).color !== linkColour()) {
        throw new Error(
            `the Categories icon must take the link colour ${linkColour()}, found ` +
                getComputedStyle(categories).color
        );
    }
}

for (const scheme of ["light", "dark"]) {
    registry.category("web_tour.tours").add(`viin_brand_lunch_search_panel_colour_${scheme}`, {
        steps: () => [
            {
                content: "the search panel of the lunch products shows its section icons",
                trigger: ".o_search_panel_section_icon[data-icon='restaurant']",
                run: () => assertSectionIconsFollowThePalette(scheme),
            },
        ],
    });
}
