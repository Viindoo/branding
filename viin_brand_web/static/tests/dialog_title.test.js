import { expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { click, queryAllTexts } from "@odoo/hoot-dom";
import {
    defineModels,
    fields,
    getService,
    makeDialogMockEnv,
    mockService,
    models,
    mountWithCleanup,
    patchTranslations,
    webModels,
} from "@web/../tests/web_test_helpers";
import {
    ClientErrorDialog,
    ErrorDialog,
    NetworkErrorDialog,
    odooExceptionTitleMap,
    RedirectWarningDialog,
    RPCErrorDialog,
    SessionExpiredDialog,
    WarningDialog,
} from "@web/core/errors/error_dialogs";
import { WebClient } from "@web/webclient/webclient";

const { ResCompany, ResPartner, ResUsers } = webModels;

const DIALOG = "@web/core/dialog/dialog";
const ACTION_DIALOG = "@web/webclient/actions/action_dialog";
const BRAND_DIALOG = "@viin_brand_web/core/dialog/dialog";

class Shop extends models.Model {
    name = fields.Char();

    _views = {
        form: `<form><field name="name"/></form>`,
    };
}

defineModels([Shop, ResCompany, ResPartner, ResUsers]);

/**
 * Evaluates the given modules on a private copy of the module registry, one after the other, the
 * way the backend bundle does it: core's dialogs first, the brand file after them. The Hoot loader
 * orders modules by their dependencies and would run the brand file first, which hides the defect.
 *
 * @param {string[]} names
 * @returns {Map<string, object>} the freshly evaluated modules
 */
function evaluateInOrder(names) {
    const { factories, modules } = odoo.loader;
    const registry = new Map(modules);
    for (const name of [DIALOG, ACTION_DIALOG, BRAND_DIALOG]) {
        registry.delete(name);
    }
    const require = (name) => {
        if (!registry.has(name)) {
            registry.set(name, factories.get(name).fn(require));
        }
        return registry.get(name);
    };
    for (const name of names) {
        require(name);
    }
    return registry;
}

test("the action dialog default title is branded when core is evaluated first and the brand file after it", () => {
    const registry = evaluateInOrder([ACTION_DIALOG, BRAND_DIALOG]);

    expect(registry.get(ACTION_DIALOG).ActionDialog.defaultProps.title).toBe("Viindoo");
});

test("a dialog opened by an action without a name reads the Viindoo brand, not Odoo", async () => {
    await mountWithCleanup(WebClient);
    await getService("action").doAction({
        type: "ir.actions.act_window",
        res_model: "shop",
        target: "new",
        views: [[false, "form"]],
    });

    expect(".o_technical_modal .modal-title").toHaveText("Viindoo");
});

async function openErrorDialog(Component, props = {}) {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(Component, {
        env,
        props: { message: "Something bad happened", traceback: "trace", close() {}, ...props },
    });
}

async function technicalTitle() {
    await click("main button");
    await animationFrame();
    return queryAllTexts("main .clearfix p")[0];
}

function expectBranded(title) {
    expect(title).toMatch(/Viindoo/);
    expect(title).not.toMatch(/Odoo/);
}

test("a business warning dialog reads the Viindoo brand, not Odoo", async () => {
    await openErrorDialog(WarningDialog);

    expectBranded(queryAllTexts("header .modal-title")[0]);
});

test("a business warning keeps the title the server gave it", async () => {
    const exceptionName = "odoo.exceptions.UserError";
    await openErrorDialog(WarningDialog, { exceptionName });

    expect("header .modal-title").toHaveText(odooExceptionTitleMap.get(exceptionName).toString());
    expect(queryAllTexts("header .modal-title")[0]).not.toMatch(/Viindoo/);
});

test("a business warning keeps the title the caller gave it", async () => {
    await openErrorDialog(WarningDialog, { title: "Caller title" });

    expect("header .modal-title").toHaveText("Caller title");
});

test("a redirect warning without a sub type reads the Viindoo brand, not Odoo", async () => {
    mockService("action", {});
    await openErrorDialog(RedirectWarningDialog, { data: { arguments: ["msg", 1, "Go", {}] } });

    expectBranded(queryAllTexts("header .modal-title")[0]);
});

test("a redirect warning keeps the sub type it was given as its title", async () => {
    mockService("action", {});
    await openErrorDialog(RedirectWarningDialog, {
        subType: "my sub type",
        data: { arguments: ["msg", 1, "Go", {}] },
    });

    expect("header .modal-title").toHaveText("My sub type");
});

test("a server error dialog reads the Viindoo brand, not Odoo", async () => {
    await openErrorDialog(RPCErrorDialog, { type: "server" });

    expectBranded(await technicalTitle());
});

test("a browser side error dialog reads the Viindoo brand, not Odoo", async () => {
    await openErrorDialog(RPCErrorDialog, { type: "script" });

    expectBranded(await technicalTitle());
});

test("a lost network error dialog reads the Viindoo brand, not Odoo", async () => {
    await openErrorDialog(RPCErrorDialog, { type: "network" });

    expectBranded(await technicalTitle());
});

test("the technical details of the generic error dialogs read the Viindoo brand", async () => {
    await openErrorDialog(ErrorDialog);

    expectBranded(await technicalTitle());
});

test("the technical details of the client error dialog read the Viindoo brand", async () => {
    await openErrorDialog(ClientErrorDialog);

    expectBranded(await technicalTitle());
});

test("the technical details of the network error dialog read the Viindoo brand", async () => {
    await openErrorDialog(NetworkErrorDialog);

    expectBranded(await technicalTitle());
});

test("the warning title is a translatable term", async () => {
    patchTranslations({ "Viindoo Warning": "SENTINEL-WARNING" });

    await openErrorDialog(WarningDialog);

    expect("header .modal-title").toHaveText("SENTINEL-WARNING");
});

test("the server error title is a translatable term", async () => {
    patchTranslations({ "Viindoo Server Error": "SENTINEL-SERVER" });

    await openErrorDialog(RPCErrorDialog, { type: "server" });

    expect(await technicalTitle()).toBe("SENTINEL-SERVER");
});

test("the session expired dialog title and message read the Viindoo brand, not Odoo", async () => {
    await openErrorDialog(SessionExpiredDialog);

    expectBranded(queryAllTexts("header .modal-title")[0]);
    expectBranded(queryAllTexts("main p")[0]);
});
