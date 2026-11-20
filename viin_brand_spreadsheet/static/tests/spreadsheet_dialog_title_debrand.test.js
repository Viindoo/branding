import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { describe, expect, test } from "@odoo/hoot";
import { makeDialogMockEnv, mountWithCleanup } from "@web/../tests/web_test_helpers";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import "@viin_brand_spreadsheet/dialog/confirmation_dialog";

describe.current.tags("desktop");
defineMailModels();

async function openDialog(title) {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(ConfirmationDialog, {
        env,
        props: { body: "Some content", title, close: () => {}, confirm: () => {} },
    });
}

test("the spreadsheet dialog is titled with the Viindoo name", async () => {
    await openDialog("Odoo Spreadsheet");
    expect(".modal-header").toHaveText("Viindoo Spreadsheet");
});

test("a dialog that merely mentions Odoo keeps its title", async () => {
    await openDialog("Odoo Studio");
    expect(".modal-header").toHaveText("Odoo Studio");
});
