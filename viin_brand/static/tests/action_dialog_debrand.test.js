import { describe, expect, test } from "@odoo/hoot";
import { queryText } from "@odoo/hoot-dom";
import { Component, xml } from "@odoo/owl";
import {
    defineModels,
    fields,
    getService,
    makeDialogMockEnv,
    models,
    mountWithCleanup,
    webModels,
} from "@web/../tests/web_test_helpers";

import { Dialog } from "@web/core/dialog/dialog";
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

// Every Dialog-family class with its own default title is listed here, so that a new class that
// copies Dialog.defaultProps fails loudly instead of shipping the stock wordmark.
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
