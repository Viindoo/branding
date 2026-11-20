import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { registry } from "@web/core/registry";
import "@viin_brand_hr_expense/js/tours/hr_expense_tour";

describe.current.tags("headless");

beforeEach(() => allowTranslations());

test("no hint of the expense tour names Odoo", () => {
    const steps = registry.category("web_tour.tours").get("hr_expense_tour").steps();
    const hints = steps.map((step) => String(step.content ?? ""));
    expect(hints.length).toBeGreaterThan(0);
    for (const hint of hints) {
        expect(hint).not.toInclude("Odoo");
    }
    expect(hints.some((hint) => hint.includes("Viindoo will save"))).toBe(true);
});
