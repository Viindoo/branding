import "@crm/js/tours/crm";
import { registry } from "@web/core/registry";

// The steps that the lead mining service adds to the tour open the Generate menu and its Lead
// Sourcing entry, which the menu does not show.
const GENERATE_MENU_TRIGGER = ".o_control_panel_main_buttons .o-dropdown";
const GENERATE_ENTRY_TRIGGER = ".o_lead_mining_element";

// A tour step is plain data: its text is rewritten in whatever language it is shown.
function nameViindoo(step) {
    const content = step.content?.toString();
    if (content && /\bOdoo\b/.test(content)) {
        return { ...step, content: content.replace(/\bOdoo\b/g, "Viindoo") };
    }
    return step;
}

/**
 * Return the steps of the tour without the lead generation steps (the Generate menu, its entry and
 * the dialog that entry opens), with Viindoo named in place of Odoo.
 */
function brandSteps(steps) {
    const result = [];
    let inLeadGeneration = false;
    for (const step of steps) {
        const trigger = typeof step.trigger === "string" ? step.trigger : "";
        if (trigger === GENERATE_MENU_TRIGGER) {
            inLeadGeneration = true;
            continue;
        }
        if (
            inLeadGeneration &&
            (trigger.startsWith(GENERATE_ENTRY_TRIGGER) || trigger.startsWith(".modal"))
        ) {
            continue;
        }
        inLeadGeneration = false;
        result.push(nameViindoo(step));
    }
    return result;
}

// The lead generation steps come from a module that patches this tour and may load before or after
// this one: the steps are filtered each time the tour is read, whatever patches it holds.
const tours = registry.category("web_tour.tours");
const crmTour = new Proxy(tours.get("crm_tour"), {
    get(target, key, receiver) {
        const value = Reflect.get(target, key, receiver);
        if (key !== "steps") {
            return value;
        }
        return function steps() {
            return brandSteps(value.apply(target, arguments));
        };
    },
});
tours.add("crm_tour", crmTour, { force: true });
