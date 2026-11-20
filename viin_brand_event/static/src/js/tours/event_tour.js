import "@event/js/tours/event_tour";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

patch(registry.category("web_tour.tours").get("event_tour"), {
    steps() {
        return super.steps(...arguments).map((step) => {
            if (typeof step.run === "string" && step.run.includes("Odoo Experience 2020")) {
                return {
                    ...step,
                    run: step.run.replace("Odoo Experience 2020", "Annual Conference 2020"),
                };
            }
            return step;
        });
    },
});
