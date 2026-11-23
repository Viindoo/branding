import { describe, expect, test } from "@odoo/hoot";
import { queryText } from "@odoo/hoot-dom";
import { Component, xml } from "@odoo/owl";
import { assignDialogTestEnv, mountWithCleanup } from "@web/../tests/web_test_helpers";

import { Dialog } from "@web/core/dialog/dialog";
import "@viin_brand/core/dialog/dialog";

describe.current.tags("desktop");

test("a dialog opened without a title renders the Viindoo wordmark, never Odoo", async () => {
    class Parent extends Component {
        static components = { Dialog };
        static template = xml`<Dialog>Content</Dialog>`;
    }
    assignDialogTestEnv();
    await mountWithCleanup(Parent);

    expect("header .modal-title").toHaveText("Viindoo");
    expect(queryText("header .modal-title")).not.toInclude("Odoo");
});

test("a dialog opened with a title keeps it", async () => {
    class Parent extends Component {
        static components = { Dialog };
        static template = xml`<Dialog title="'Confirm'">Content</Dialog>`;
    }
    assignDialogTestEnv();
    await mountWithCleanup(Parent);

    expect("header .modal-title").toHaveText("Confirm");
});
