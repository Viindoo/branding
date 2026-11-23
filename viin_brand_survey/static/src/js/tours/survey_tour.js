import { markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import "@survey/js/tours/survey_tour";

const tour = registry.category("web_tour.tours").get("survey_tour");
const coreSteps = tour.steps;

function rebrand(content) {
    const text = String(content).replaceAll("Odoo", "Viindoo");
    return typeof content === "string" ? text : markup(text);
}

// The hint of the answer step names the product: the wordmark is rewritten.
tour.steps = (...args) =>
    coreSteps(...args).map((step) =>
        String(step.content ?? "").includes("Odoo")
            ? { ...step, content: rebrand(step.content) }
            : step
    );
