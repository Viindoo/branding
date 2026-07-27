import { describe, expect, test } from "@odoo/hoot";
import { queryText } from "@odoo/hoot-dom";
import { Component, xml } from "@odoo/owl";
import { makeDialogMockEnv, mountWithCleanup } from "@web/../tests/web_test_helpers";

import { Dialog } from "@web/core/dialog/dialog";
// ActionDialog builds its own defaults with `{ ...Dialog.defaultProps, withBodyPadding: false }`
// (web/static/src/webclient/actions/action_dialog.js:17-20). That spread SNAPSHOTS the title at
// class-definition time, and OWL applies `component.constructor.defaultProps` at render
// (web/static/lib/owl/owl.js:2600) - so the snapshot, not the live base value, is what users see.
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// Side-effect import of the REAL, unmodified viin_brand_web patch, exactly as production loads it.
// The module is already in web.assets_backend (which web.assets_unit_tests_setup includes), so this
// import does not re-run it - the loader caches modules and ignores duplicate defines. The patch
// therefore executes at its true production position in the bundle, which is precisely what makes
// these tests a faithful proof of the real load order rather than an artificial one.
import "@viin_brand_web/core/dialog/dialog";

describe.tags("desktop");

// Business rule under protection: NO backend dialog may fall back to the stock Odoo wordmark once
// viin_brand_web is installed. `dialog_debrand.test.js` guards the base Dialog default; these tests
// guard the rendered outcome, including the ActionDialog snapshot that the base patch cannot reach.
// An act_window with target="new" and no `name` never sets a title prop
// (web/static/src/webclient/actions/action_service.js:1069-1071), so this default really renders.

test("ActionDialog opened without a title renders the Viindoo wordmark, never Odoo", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(ActionDialog, { env, props: { close: () => {} } });

    expect(".o_dialog").toHaveCount(1);
    expect("header .modal-title").toHaveText("Viindoo");
    expect(queryText("header .modal-title")).not.toInclude("Odoo");
});

test("Dialog opened without a title renders the Viindoo wordmark, never Odoo", async () => {
    class Parent extends Component {
        static components = { Dialog };
        static template = xml`<Dialog>Content</Dialog>`;
        static props = ["*"];
    }
    await makeDialogMockEnv();
    await mountWithCleanup(Parent);

    expect("header .modal-title").toHaveText("Viindoo");
    expect(queryText("header .modal-title")).not.toInclude("Odoo");
});

// Cheap static sweep over every Dialog-family class known to carry its own default title. If core
// adds another class that snapshots Dialog.defaultProps, add it here: this is the one place that
// makes such a leak fail loudly instead of silently shipping the stock wordmark.
test("no Dialog-family default title carries the Odoo wordmark", () => {
    const targets = [
        ["Dialog", Dialog],
        ["ActionDialog", ActionDialog],
    ];
    for (const [label, cls] of targets) {
        expect(cls.defaultProps.title).not.toInclude("Odoo", {
            message: `${label}.defaultProps.title must not carry the Odoo wordmark`,
        });
    }
});
