import { describe, expect, test } from "@odoo/hoot";

// Core Dialog ships `static defaultProps = { ... title: "Odoo" }` (web/static/src/core/dialog/dialog.js).
import { Dialog } from "@web/core/dialog/dialog";
// Side-effect import of the REAL viin_brand_web patch, exactly as production loads it: it rewrites
// the Odoo wordmark via replaceAll - but only after asserting the core default is still a string
// carrying that wordmark, otherwise leaving the value untouched and reporting via console.error.
// It now covers the ActionDialog snapshot too (see action_dialog_debrand.test.js). Importing it
// here runs the mutation inside the unit-test bundle before any test body executes (same idiom
// as viin_brand_pos's guard test).
import "@viin_brand_web/core/dialog/dialog";

describe.current.tags("headless");

// Business rule under protection: after viin_brand_web assets load, a backend Dialog opened with
// NO explicit title must fall back to the "System" brand - never the stock "Odoo" default. This is
// the de-brand contract of static/src/core/dialog/dialog.js. If that patch is dropped or stops
// matching the core default, `title` stays "Odoo" and this test goes red for the right reason.
// Expected value updated to "System" per owner decision D3 (unify the Dialog/ActionDialog title
// wordmark with the error/crash-dialog family, which already used "System").
test("backend dialog default title is de-branded to System, never Odoo", () => {
    expect(Dialog.defaultProps.title).toBe("System");
    expect(Dialog.defaultProps.title).not.toInclude("Odoo");
});
