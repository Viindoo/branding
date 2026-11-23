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

// The steps that the lead mining service adds to the tour.
const LEAD_MINING_STEPS = [
    { trigger: ".o_control_panel_main_buttons .o-dropdown", run: "click" },
    {
        trigger: '.o_lead_mining_element[data-module-xml-id="base.module_crm_iap_mine"]',
        run: "click",
    },
    { trigger: ".modal-body .o_industry", run: "click" },
    { trigger: ".modal-footer button[name=action_submit]", run: "click" },
    { trigger: ".modal-footer button[special=cancel]", run: "click" },
];

test("the crm onboarding tour does not name Odoo and names Viindoo instead", () => {
    const steps = registry.category("web_tour.tours").get("crm_tour").steps();

    expect(steps.length).toBeGreaterThan(0);
    for (const step of steps) {
        expect(String(step.content || "")).not.toInclude("Odoo");
    }
    expect(steps.map((step) => String(step.content || "")).join(" ")).toMatch(/\bViindoo\b/);
});

test("the crm onboarding tour leaves out the lead generation steps the lead mining service adds", () => {
    const tour = registry.category("web_tour.tours").get("crm_tour");
    const triggers = () => tour.steps().map((step) => step.trigger);
    const withoutLeadMining = triggers();
    patchWithCleanup(tour, {
        steps() {
            return [...super.steps(), ...LEAD_MINING_STEPS];
        },
    });

    expect(triggers()).toEqual(withoutLeadMining);
    expect(triggers()).toInclude('.modal-footer button[name="action_schedule_activities"]');
});

test("the probability tooltip names Viindoo as the computing product and links to a Viindoo page", async () => {
    await mountWithCleanup(CrmPlsTooltip, {
        props: { dashArrayVals: "10 20", probability: 40, top3Data: [], low3Data: [] },
    });

    expect(".o_crm_pls_tooltip_footer").not.toHaveText(/Odoo/);
    expect(".o_crm_pls_tooltip_footer").toHaveText(/\bViindoo\b/);
    expect(".o_crm_pls_tooltip_footer a").toHaveAttribute("href", /^https:\/\/viindoo\.com\//);
});
