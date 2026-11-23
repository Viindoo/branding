// Realigns the favorite management tour of core (web, "test_favorite_management") to the Apps of
// Viindoo, which do not group the modules by the apps store of Odoo.
//
// The tour saves the favorite "Apps1" from the default facets of the Apps and edits the first rule
// of its domain. Core saves that rule from the group of the search panel by module type, which the
// Apps of Viindoo do not offer (models/ir_module_module.py), so the domain of the favorite is empty
// and the editor starts with no rule: the realignment adds the rule that the editor then edits. Every
// other step of the tour runs as core writes it.

import { registry } from "@web/core/registry";

const TOUR_NAME = "test_favorite_management";
const OPEN_DOMAIN_EDITOR = ".o_field_domain > div > div";

const tours = registry.category("web_tour.tours");
const coreTour = tours.get(TOUR_NAME);

tours.add(
    TOUR_NAME,
    {
        ...coreTour,
        steps: (...args) => {
            const steps = coreTour.steps(...args);
            const index = steps.findIndex((step) => step.trigger === OPEN_DOMAIN_EDITOR);
            if (index < 0) {
                throw new Error(
                    `the step "${OPEN_DOMAIN_EDITOR}" of the tour ${TOUR_NAME} is gone`
                );
            }
            steps.splice(index + 1, 0, {
                content: "The favorite has no rule of the module type: add the rule to edit",
                trigger: ".o_field_domain button:contains(New Rule)",
                run: "click",
            });
            return steps;
        },
    },
    { force: true }
);
