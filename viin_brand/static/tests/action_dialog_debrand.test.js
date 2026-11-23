import { describe, expect, test } from "@odoo/hoot";
import { queryText } from "@odoo/hoot-dom";
import {
    assignDialogTestEnv,
    defineModels,
    fields,
    getService,
    models,
    mountWithCleanup,
    webModels,
} from "@web/../tests/web_test_helpers";

import { ActionDialog } from "@web/webclient/actions/action_dialog";
import { WebClient } from "@web/webclient/webclient";
import "@viin_brand/core/dialog/dialog";
import "@viin_brand/webclient/actions/action_dialog";

const { ResCompany, ResPartner, ResUsers } = webModels;

class Shop extends models.Model {
    name = fields.Char();

    _views = {
        form: `<form><field name="name"/></form>`,
    };
}

defineModels([Shop, ResCompany, ResPartner, ResUsers]);

describe.current.tags("desktop");

// An act_window with target="new" and no `name` never sets a title prop, so the default title is
// what renders. The ActionDialog case mounts the class directly; the action-service case drives
// the real user path.

test("ActionDialog opened without a title renders the Viindoo wordmark, never Odoo", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(ActionDialog, { props: { close: () => {} } });

    expect(".o_dialog").toHaveCount(1);
    expect("header .modal-title").toHaveText("Viindoo");
    expect(queryText("header .modal-title")).not.toInclude("Odoo");
});

test("a dialog opened by an action without a name renders the Viindoo wordmark, never Odoo", async () => {
    await mountWithCleanup(WebClient);
    await getService("action").doAction({
        type: "ir.actions.act_window",
        res_model: "shop",
        target: "new",
        views: [[false, "form"]],
    });

    expect(".o_technical_modal .modal-title").toHaveText("Viindoo");
});
