import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { registry } from "@web/core/registry";
import "@viin_brand_survey/js/tours/survey_tour";

describe.current.tags("headless");

beforeEach(() => allowTranslations());

test("no hint of the survey tour names Odoo", () => {
    const hints = registry
        .category("web_tour.tours")
        .get("survey_tour")
        .steps()
        .map((step) => String(step.content ?? ""));
    expect(hints.length).toBeGreaterThan(0);
    for (const hint of hints) {
        expect(hint).not.toInclude("Odoo");
    }
    expect(hints.some((hint) => hint.includes("Viindoo saves it for you"))).toBe(true);
});
