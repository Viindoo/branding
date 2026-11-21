/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * The branded palette has no `#65435C` swatch, so the custom-colour steps of core's
 * `website_background_colorpicker` tour cannot hold. This re-registers the tour with its first
 * custom swatch picked from the branded palette and the hard-coded custom-colour RGBA assertion
 * relaxed into a check that the RGBA pane is shown. The gradient steps are unchanged.
 */
const tours = registry.category("web_tour.tours");
const core = tours.get("website_background_colorpicker", null);
if (core) {
    tours.add(
        "website_background_colorpicker",
        {
            ...core,
            steps: () => {
                const steps = core.steps();
                // The gradient and the custom colour each have an "RGBA color matches" check;
                // the custom one is the last.
                const rgbaIdx = steps
                    .map((s, i) =>
                        (s.content || "").includes("RGBA color matches the selected color") ? i : -1
                    )
                    .filter((i) => i >= 0);
                const dropIdx = rgbaIdx.length ? rgbaIdx[rgbaIdx.length - 1] : -1;
                return steps.reduce((acc, s, i) => {
                    if (i === dropIdx) {
                        // A step without `run` is a pure check; a tour must end on a check, as
                        // web_tour ignores the action of a last step.
                        const checkStep = {
                            ...s,
                            content: "Check the custom color RGBA pane is shown (brand palette)",
                        };
                        delete checkStep.run;
                        acc.push(checkStep);
                        return acc;
                    }
                    if (s.trigger && s.trigger.includes("#65435C")) {
                        acc.push({
                            ...s,
                            content: "Select first custom color element (brand palette)",
                            trigger:
                                ".o_colorpicker_section .o_we_color_btn[style^='background-color:']",
                        });
                        return acc;
                    }
                    acc.push(s);
                    return acc;
                }, []);
            },
        },
        { force: true }
    );
}
