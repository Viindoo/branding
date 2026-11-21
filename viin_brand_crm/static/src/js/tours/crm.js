import "@crm/js/tours/crm";
import { registry } from "@web/core/registry";

// The Lead Generation button is removed from the leads, so the tour cannot wait for it.
const LEAD_GENERATION_TRIGGER = ".o_button_generate_leads";

// A tour step is plain data: its text is rewritten in whatever language it is shown.
function nameViindoo(step) {
    const content = step.content?.toString();
    if (content && /\bOdoo\b/.test(content)) {
        return { ...step, content: content.replace(/\bOdoo\b/g, "Viindoo") };
    }
    return step;
}

/**
 * Return the steps of the tour without the Lead Generation step and the steps of the dialog that
 * step opens, with Viindoo named in place of Odoo.
 */
function brandSteps(steps) {
    const result = [];
    let inLeadGenerationDialog = false;
    for (const step of steps) {
        if (step.trigger.includes(LEAD_GENERATION_TRIGGER)) {
            inLeadGenerationDialog = true;
            continue;
        }
        if (inLeadGenerationDialog && step.trigger.startsWith(".modal")) {
            continue;
        }
        inLeadGenerationDialog = false;
        result.push(nameViindoo(step));
    }
    return result;
}

// The Lead Generation steps come from a module that patches this tour and may load before or after
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
