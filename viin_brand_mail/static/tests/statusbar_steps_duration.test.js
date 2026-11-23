import { mailModels, openFormView, start, startServer } from "@mail/../tests/mail_test_helpers";
import { ResPartner } from "@mail/../tests/mock_server/mock_models/res_partner";
import { describe, expect, test } from "@odoo/hoot";
import { queryAll, queryAllAttributes } from "@odoo/hoot-dom";
import { defineModels, fields, models } from "@web/../tests/web_test_helpers";

// Business rule under protection: the steps of the duration statusbars of mail (`statusbar_duration`
// and `rotting_statusbar_duration`, primary copies of core's statusbar) show their ordinal in the
// order a user reads them, like the statusbar of core does. The numbers come from
// `viinStepNumber()` of viin_brand, reached through an attribute the two templates of this module
// add; the DOM order of the steps is the reverse of their reading order, so only a mounted view
// tells a right number from a reversed one.
import "@viin_brand/views/fields/statusbar/statusbar_steps";

describe.current.tags("desktop");

const STAGES = ["New", "Qualified", "Proposition", "Won"];

async function openPartnerWithStages(widget) {
    class Stage extends models.Model {
        _name = "stage";
        name = fields.Char();
    }
    ResPartner._fields.stage_id = fields.Many2one({ relation: "stage" });
    ResPartner._fields.duration_tracking = fields.Json();
    ResPartner._fields.is_rotting = fields.Boolean();
    ResPartner._fields.rotting_days = fields.Integer();
    defineModels({ ...mailModels, ResPartner, Stage });
    const pyEnv = await startServer();
    const stageIds = pyEnv["stage"].create(STAGES.map((name) => ({ name })));
    const partnerId = pyEnv["res.partner"].create({
        name: "John Doe",
        stage_id: stageIds[2],
        duration_tracking: { [stageIds[0]]: 90, d: "2026-03-11 05:12:22", s: stageIds[2] },
    });
    await start();
    await openFormView("res.partner", partnerId, {
        arch: `<form>
            <field name="is_rotting" invisible="1"/>
            <!-- read by the rotting statusbar widget, never shown -->
            <field name="rotting_days" invisible="1"/>
            <!-- read by the rotting statusbar widget, never shown -->
            <field name="stage_id" widget="${widget}"/>
        </form>`,
    });
}

/** Visible inline steps, left to right - the order a user reads them, not the DOM order. */
function visibleStepsInReadingOrder() {
    return queryAll(
        ".o_statusbar_status button.o_arrow_button:not(.dropdown-toggle):not(.d-none)"
    ).sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
}

for (const widget of ["statusbar_duration", "rotting_statusbar_duration"]) {
    test(`the steps of ${widget} are numbered in reading order, not in DOM order`, async () => {
        await openPartnerWithStages(widget);

        const steps = visibleStepsInReadingOrder();
        expect(steps.length).toBe(STAGES.length);
        expect(steps.map((step) => step.dataset.viinStep)).toEqual(["1", "2", "3", "4"]);
        // The ordinal labels the stage: each step names the stage of its rank.
        STAGES.forEach((stage, index) => expect(steps[index].textContent).toInclude(stage));
    });

    test(`the numbers of ${widget} leave the current step and the radio semantics of core intact`, async () => {
        await openPartnerWithStages(widget);

        expect(".o_statusbar_status button.o_arrow_button_current").toHaveCount(1);
        expect(".o_statusbar_status button.o_arrow_button_current").toHaveAttribute(
            "data-viin-step",
            "3"
        );
        expect(
            queryAllAttributes(
                ".o_statusbar_status button.o_arrow_button:not(.dropdown-toggle)",
                "role"
            )
        ).toEqual(["radio", "radio", "radio", "radio"]);
    });
}
