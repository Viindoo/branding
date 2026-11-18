import { describe, expect, test } from "@odoo/hoot";
import { queryAll, queryAllAttributes, queryAllTexts } from "@odoo/hoot-dom";
import { defineModels, fields, models, mountView } from "@web/../tests/web_test_helpers";

// Business rule under protection: every step of the form-header statusbar shows its ordinal,
// numbered in the order a user reads them, on core's arrow steps - and adding those numbers
// changes nothing else about the widget.
//
// This is a DOM test because the compiled-CSS guard
// (tests/test_brand_cascade_compile.py::
// test_statusbar_steps_render_a_numbered_marker_that_inherits_its_step_label_colour) proves the
// `content: attr(data-viin-step)` rule is in both bundles and that what it inherits clears AA, but
// not that the numbers are right: the attribute is produced by viinStepNumber(), and the
// statusbar's DOM order is the reverse of its visual order (getSortedItems() reverses
// `items.inline`, and the row is laid out `flex-flow: row-reverse`). An off-by-reverse bug
// compiles and renders "3 2 1" left to right; only a mounted view catches it.
//
// Importing the production JS + XML as side effects makes the patch and the template extension
// live in the Hoot runtime.
import "@viin_brand/views/fields/statusbar/statusbar_steps";

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
    // The numbering follows the selection order, so the ordinal labels the stage.
    expect(steps.map((el) => el.textContent.trim())).toEqual(["New", "Qualified", "Won"]);
});

test("the number is generated content, so the step's DOM text stays exactly core's label", async () => {
    // The template adds an attribute rather than a <span> because core's own suite and the sale /
    // crm tours assert statusbar text exactly; a digit in a text node would append itself to every
    // one of those assertions. The texts are in DOM order, the reverse of reading order.
    await mountView({ type: "form", resModel: "lead", resId: 1, arch: ARCH });

    expect(queryAllTexts(".o_statusbar_status button.o_arrow_button:not(.d-none)")).toEqual([
        "Won",
        "Qualified",
        "New",
    ]);
});

test("adding the numbers leaves core's step markup and current-step state intact", async () => {
    await mountView({ type: "form", resModel: "lead", resId: 1, arch: ARCH });

    // The hook class is additive: core's own classes and the current-step flag are untouched.
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
