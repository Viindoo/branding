import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { registry } from "@web/core/registry";
import "@viin_brand_event/js/tours/event_tour";

describe.current.tags("headless");

beforeEach(() => {
    allowTranslations();
});

test("the events onboarding tour does not type the Odoo name", () => {
    const steps = registry.category("web_tour.tours").get("event_tour").steps();

    expect(steps.length).toBeGreaterThan(0);
    for (const step of steps) {
        expect(String(step.run ?? "")).not.toInclude("Odoo");
        expect(String(step.run ?? "")).not.toInclude("Viindoo");
    }
    expect(steps.map((step) => String(step.run ?? "")).join(" ")).toInclude(
        "edit Annual Conference 2020"
    );
});
