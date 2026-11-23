import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { getService, mountWithCleanup } from "@web/../tests/web_test_helpers";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { DialogPlugin } from "@web/core/dialog/dialog_plugin";
import { MainComponentsContainer } from "@web/core/main_components_container";
import "@viin_brand_spreadsheet/dialog/spreadsheet_dialog_title";

describe.current.tags("desktop");
defineMailModels();

async function openDialog(title) {
    await mountWithCleanup(MainComponentsContainer);
    getService(DialogPlugin).add(ConfirmationDialog, {
        body: "Some content",
        title,
        confirm: () => {},
    });
    await animationFrame();
}

test("the spreadsheet dialog is titled with the Viindoo name", async () => {
    await openDialog("Odoo Spreadsheet");
    expect(".modal-header").toHaveText("Viindoo Spreadsheet");
});

test("a dialog that merely mentions Odoo keeps its title", async () => {
    await openDialog("Odoo Studio");
    expect(".modal-header").toHaveText("Odoo Studio");
});
