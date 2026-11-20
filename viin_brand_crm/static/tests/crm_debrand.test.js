import { beforeEach, describe, expect, test } from "@odoo/hoot";
import {
    allowTranslations,
    mountWithCleanup,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { registry } from "@web/core/registry";
import { defineCrmModels } from "@crm/../tests/crm_test_helpers";
import { CrmPlsTooltip } from "@crm/views/crm_form/crm_pls_tooltip_button";
import "@viin_brand_crm/js/tours/crm";

describe.current.tags("headless");

defineCrmModels();

beforeEach(() => {
    allowTranslations();
});

test("the crm onboarding tour does not name Odoo", () => {
    const steps = registry.category("web_tour.tours").get("crm_tour").steps();

    expect(steps.length).toBeGreaterThan(0);
    for (const step of steps) {
        expect(String(step.content || "")).not.toInclude("Odoo");
    }
    expect(steps.map((step) => String(step.content || "")).join(" ")).toInclude(
        "Viindoo will save all modifications"
    );
});

test("the crm onboarding tour leaves out the Lead Generation steps of the hidden button", () => {
    const tour = registry.category("web_tour.tours").get("crm_tour");
    // the steps the lead mining service adds to the tour
    patchWithCleanup(tour, {
        steps() {
            return [
                ...super.steps(),
                { trigger: ".o_button_generate_leads", run: "click .o_button_generate_leads" },
                { trigger: ".modal-body .o_industry", run: "click" },
                { trigger: ".modal-footer button[name=action_submit]", run: "click" },
                { trigger: ".modal-footer button[special=cancel]", run: "click" },
                { trigger: ".o_kanban_view", run: "click" },
            ];
        },
    });

    const triggers = tour.steps().map((step) => step.trigger);

    expect(triggers).not.toInclude(".o_button_generate_leads");
    expect(triggers).not.toInclude(".modal-body .o_industry");
    expect(triggers).not.toInclude(".modal-footer button[name=action_submit]");
    expect(triggers).not.toInclude(".modal-footer button[special=cancel]");
    expect(triggers).toInclude('.modal-footer button[name="action_schedule_activities"]');
    expect(triggers.at(-1)).toBe(".o_kanban_view");
});

test("the probability tooltip names Viindoo as the computing product and links to a Viindoo page", async () => {
    await mountWithCleanup(CrmPlsTooltip, {
        props: { dashArrayVals: "10 20", probability: 40, top3Data: [], low3Data: [] },
    });

    expect(".o_crm_pls_tooltip_footer").not.toHaveText(/Odoo/);
    expect(".o_crm_pls_tooltip_footer").toHaveText(/Computed by Viindoo from your data\./);
    expect(".o_crm_pls_tooltip_footer a").toHaveAttribute("href", /^https:\/\/viindoo\.com\//);
});
