/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * viin_brand_common recolours the frontend theme palette (primary #7f4282), so
 * the core `website_background_colorpicker` tour no longer holds on the branded
 * stack: its custom-colour step targets a hard-coded swatch
 * `background-color:#65435C` (= rgb(101,67,92)) which the recoloured palette
 * never produces, and its following RGBA check asserts that exact rgb.
 *
 * Re-register the tour (force) with the custom-colour part adapted to whatever
 * the first custom swatch is on the branded palette, and relax only the
 * hard-coded custom-colour RGBA assertion into a pure check that the RGBA pane
 * rendered (a plain drop would leave a click step as the LAST step, and
 * web_tour ignores the action of a last step with a warning). The gradient
 * steps (a fixed preset, unaffected by branding) and their RGBA check are kept
 * intact, so the tour still exercises the colorpicker.
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
                // Indices of both "RGBA color matches" checks (gradient + custom);
                // the custom one is the last such step.
                const rgbaIdx = steps
                    .map((s, i) =>
                        (s.content || "").includes("RGBA color matches the selected color") ? i : -1
                    )
                    .filter((i) => i >= 0);
                const dropIdx = rgbaIdx.length ? rgbaIdx[rgbaIdx.length - 1] : -1;
                return steps.reduce((acc, s, i) => {
                    if (i === dropIdx) {
                        // Relax the hard-coded custom-colour rgb assertion into a
                        // pure check: the branded palette produces a different rgb,
                        // but the tour must still END on a step that actually
                        // asserts something rather than on a bare action.
                        //
                        // 17.0 expressed "this is a check step" as `isCheck: true`
                        // plus `run: undefined`. Neither survives at 18.0: the tour
                        // engine was rewritten (TourAutomatic/TourStepAutomatic) and
                        // its StepSchema (web_tour/static/src/tour_service/
                        // tour_service.js) has no isCheck key at all, so an Owl
                        // validate() pass would reject the step. `run` is declared
                        // optional with type [String, Function, Boolean], so an
                        // explicit undefined is not the same as absent either.
                        // The 18.0 idiom is simply a step carrying no run at all -
                        // core's own tours end that way.
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
