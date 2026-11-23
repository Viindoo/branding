import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";

describe.current.tags("headless");

const BRAND_NAME = /\bOdoo\b|odoo\.com|odoo-mobile/i;

const shown = (template) => [
    template.textContent,
    ...[...template.querySelectorAll("img")].flatMap((img) => [
        img.getAttribute("src"),
        img.getAttribute("data-original-src"),
        img.getAttribute("alt"),
    ]),
];

test("the sample snippets of the builder show no Odoo image nor wording", () => {
    for (const name of ["s_section_mobile", "s_customer_quote", "s_schedule", "s_call_to_action"]) {
        const template = getTemplate(`mass_mailing.${name}`);
        // the store badges are neutral images hosted by the CDN of the core
        const text = shown(template)
            .filter((value) => !String(value).includes("odoocdn.com"))
            .join(" ");
        expect(text).not.toMatch(BRAND_NAME);
    }
});

test("the app advertising block shows a neutral mobile mockup with placeholder store links", () => {
    const template = getTemplate("mass_mailing.s_section_mobile");
    const mockup = template.querySelector("img.o_editable_media");
    expect(mockup.getAttribute("src")).toBe(
        "/viin_brand_mass_mailing/static/src/img/mobile-app.png"
    );
    const links = [...template.querySelectorAll("a[target='_blank']")];
    expect(links.map((link) => link.getAttribute("href"))).toEqual(["#", "#"]);
    expect(links.map((link) => link.querySelector("img").getAttribute("alt"))).toEqual([
        "Google Play Store",
        "App Store",
    ]);
});

test("the schedule snippet lists a neutral demo", () => {
    const template = getTemplate("mass_mailing.s_schedule");
    expect(template.textContent).not.toInclude("Viindoo");
    expect(template.textContent).not.toMatch(BRAND_NAME);
});

test("the call to action block is sample copy of the customer", () => {
    const template = getTemplate("mass_mailing.s_call_to_action");
    const text = template.textContent.replace(/\s+/g, " ");
    expect(text).not.toInclude("Viindoo");
    expect(text).not.toMatch(BRAND_NAME);
});
