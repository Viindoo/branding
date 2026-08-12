import { describe, expect, test } from "@odoo/hoot";
import { queryAll, queryAllAttributes, queryAllTexts } from "@odoo/hoot-dom";
import { defineModels, fields, models, mountView } from "@web/../tests/web_test_helpers";

// Business rule under protection (owner 2026-08-03): every step of the form-header statusbar shows
// its ORDINAL, numbered in the order a user reads them, ON core's arrow steps - and adding those
// numbers changes nothing else about the widget.
//
// WHY A DOM TEST AND NOT ONLY THE COMPILED-CSS GUARD. The sibling Python guard
// (tests/test_brand_cascade_compile.py::
// test_statusbar_steps_render_a_numbered_marker_that_inherits_its_step_label_colour) proves the
// `content: attr(data-viin-step)` rule is in both bundles and that what it inherits clears AA. It
// cannot prove the numbers are RIGHT: the attribute is produced by viinStepNumber(), and the whole
// reason that getter exists is that the statusbar's DOM order is the REVERSE of its visual order
// (getSortedItems() reverses `items.inline`, and the row is laid out `flex-flow: row-reverse`). An
// off-by-reverse bug compiles perfectly and renders "3 2 1" left to right. Only a mounted view
// catches it, which is what this file does.
//
// Importing the production JS + XML as side effects mirrors the idiom the sibling debrand tests
// use, so the patch and the template extension are live in the Hoot runtime.
import "@viin_brand_common/views/fields/statusbar/statusbar_steps";

describe.current.tags("desktop");

class Lead extends models.Model {
    name = fields.Char();
    stage = fields.Selection({
        selection: [
            ["new", "New"],
            ["qualified", "Qualified"],
            ["won", "Won"],
        ],
        default: "qualified",
    });

    _records = [{ id: 1, name: "a lead", stage: "qualified" }];
}

defineModels([Lead]);

const ARCH = /* xml */ `
    <form>
        <header>
            <field name="stage" widget="statusbar"/>
        </header>
    </form>
`;

/** Visible inline steps, left to right - the order a user reads them, not the DOM order. */
function visibleStepsInReadingOrder() {
    return queryAll(
        ".o_statusbar_status button.o_arrow_button:not(.dropdown-toggle):not(.d-none)"
    ).sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
}

test("every statusbar step is numbered in reading order, not in DOM order", async () => {
    await mountView({ type: "form", resModel: "lead", resId: 1, arch: ARCH });

    const steps = visibleStepsInReadingOrder();
    expect(steps.length).toBe(3);
    expect(steps.map((el) => el.dataset.viinStep)).toEqual(["1", "2", "3"]);
    // ... and the numbering follows the SELECTION order, so the ordinal actually labels the stage.
    expect(steps.map((el) => el.textContent.trim())).toEqual(["New", "Qualified", "Won"]);
});

test("the number is generated content, so the step's DOM text stays exactly core's label", async () => {
    // The reason the template adds an ATTRIBUTE rather than a <span>: core's own suite asserts
    // statusbar text exactly (web/static/tests/views/fields/statusbar_field.test.js:
    // `expect(".o_arrow_button_current").toHaveText("first record")`), and so do the sale / crm
    // tours. A digit in a text node would append itself to every one of those assertions.
    // Asserted in DOM order (which is the reverse of reading order) on purpose - that is what
    // queryAllTexts returns, and spelling it out documents the reversal the ordinals correct for.
    await mountView({ type: "form", resModel: "lead", resId: 1, arch: ARCH });

    expect(queryAllTexts(".o_statusbar_status button.o_arrow_button:not(.d-none)")).toEqual([
        "Won",
        "Qualified",
        "New",
    ]);
});

test("adding the numbers leaves core's step markup and current-step state intact", async () => {
    await mountView({ type: "form", resModel: "lead", resId: 1, arch: ARCH });

    // The hook class is ADDITIVE: core's own classes and the current-step flag are untouched.
    expect(".o_statusbar_status button.o_arrow_button_current").toHaveCount(1);
    expect(".o_statusbar_status button.o_arrow_button_current").toHaveAttribute(
        "data-viin-step",
        "2"
    );
    expect(".o_statusbar_status button.o_arrow_button_current").toHaveClass([
        "btn",
        "btn-secondary",
        "o_arrow_button",
        "o_viin_numbered_step",
    ]);
    // Core keeps driving the radiogroup semantics; the marker adds none of its own.
    expect(".o_statusbar_status button.o_arrow_button_current").toHaveAttribute(
        "aria-current",
        "step"
    );
    expect(
        queryAllAttributes(
            ".o_statusbar_status button.o_arrow_button:not(.dropdown-toggle)",
            "role"
        )
    ).toEqual(["radio", "radio", "radio"]);
});
