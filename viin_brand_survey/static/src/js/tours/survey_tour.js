import { markup } from "@odoo/owl";
import { registry } from "@web/core/registry";

const tour = registry.category("web_tour.tours").get("survey_tour");
const coreSteps = tour.steps;

// The hint of the answer step names the product: the wordmark is rewritten.
tour.steps = (...args) =>
    coreSteps(...args).map((step) =>
        String(step.content ?? "").includes("Odoo")
            ? { ...step, content: markup(String(step.content).replaceAll("Odoo", "Viindoo")) }
            : step
    );
