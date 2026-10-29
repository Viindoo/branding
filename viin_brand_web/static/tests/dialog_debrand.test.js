import { describe, expect, test } from "@odoo/hoot";

// Core Dialog ships `static defaultProps = { ... title: "Odoo" }`.
import { Dialog } from "@web/core/dialog/dialog";
// Side-effect import of the REAL viin_brand_web patch, exactly as production loads it: it rewrites
// the Odoo wordmark via replaceAll - but only after asserting the core default is still a string
// carrying that wordmark, otherwise leaving the value untouched and reporting via console.error.
// Importing it here runs the mutation inside the unit-test bundle before any test body executes.
import "@viin_brand_web/core/dialog/dialog";

describe.current.tags("headless");

// Business rule under protection: after viin_brand_web assets load, a backend Dialog opened with
// NO explicit title must fall back to the "Viindoo" wordmark - never the stock "Odoo" default. If
// the patch is dropped or stops matching the core default, `title` stays "Odoo" and this test goes
// red for the right reason.
test("backend dialog default title is de-branded to Viindoo, never Odoo", () => {
    expect(Dialog.defaultProps.title).toBe("Viindoo");
    expect(Dialog.defaultProps.title).not.toInclude("Odoo");
});
