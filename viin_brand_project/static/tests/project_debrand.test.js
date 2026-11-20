import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { getTemplate } from "@web/core/templates";
import { registry } from "@web/core/registry";
import "@viin_brand_project/js/tours/project_tour";

describe.current.tags("headless");

beforeEach(() => allowTranslations());

test("no hint of the project tour names Odoo", () => {
    const hints = registry
        .category("web_tour.tours")
        .get("project_tour")
        .steps()
        .map((step) => String(step.content ?? ""));
    expect(hints.length).toBeGreaterThan(0);
    for (const hint of hints) {
        expect(hint).not.toInclude("Odoo");
    }
    expect(hints.some((hint) => hint.includes("Viindoo will automatically save"))).toBe(true);
});

test("the customer feedback example of the stage columns names Viindoo", () => {
    const template = getTemplate("project.example.customerfeedback");
    expect(template.textContent).toInclude("Viindoo creates tasks automatically");
    expect(template.textContent).not.toInclude("Odoo");
});
