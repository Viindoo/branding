import { markup } from "@odoo/owl";
import { registry } from "@web/core/registry";

const tour = registry.category("web_tour.tours").get("hr_expense_tour");
const coreSteps = tour.steps;

// The save hint of the tour names the product: the wordmark is rewritten and the markup kept.
tour.steps = (...args) =>
    coreSteps(...args).map((step) =>
        String(step.content ?? "").includes("Odoo")
            ? { ...step, content: markup(String(step.content).replaceAll("Odoo", "Viindoo")) }
            : step
    );
