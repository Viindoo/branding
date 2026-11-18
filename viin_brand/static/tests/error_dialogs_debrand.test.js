import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { click, queryAllTexts, queryText } from "@odoo/hoot-dom";
import { makeDialogMockEnv, mockService, mountWithCleanup } from "@web/../tests/web_test_helpers";

// The error dialogs of core carry the Odoo wordmark in their titles and in the technical details;
// viin_brand replaces it with "Viindoo" across the whole family.
import {
    ClientErrorDialog,
    NetworkErrorDialog,
    RedirectWarningDialog,
    RPCErrorDialog,
    WarningDialog,
} from "@web/core/errors/error_dialogs";
import "@viin_brand/core/errors/error_dialogs";

describe.current.tags("desktop");

// The technical-details panel of core's web.ErrorDialog renders the title, the name, the message,
// the context details and the traceback, and stays collapsed until "See technical details" is
// clicked. The dialog header always reads "Oops!", so the wordmark under test lives in the panel.

// A genuine client-side crash shows the bold technical-details title with the Viindoo wordmark.
test("ClientErrorDialog technical-details title carries the Viindoo wordmark, never bare", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(ClientErrorDialog, {
        env,
        props: {
            message: "Something bad happened",
            name: "ERROR_NAME",
            traceback: "This is a traceback string",
            close() {},
        },
    });

    expect("div.o_error_detail").toHaveCount(0);
    await click("main button");
    await animationFrame();
    expect("div.o_error_detail").toHaveCount(1);

    const [titleText] = queryAllTexts("main .clearfix p");
    expect(titleText).toMatch(/^Viindoo /);
    expect(titleText).not.toInclude("Odoo");
});

// Same rule for the NetworkErrorDialog.
test("NetworkErrorDialog technical-details title carries the Viindoo wordmark, never bare", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(NetworkErrorDialog, {
        env,
        props: {
            message: "Could not reach the server",
            name: "ERROR_NAME",
            traceback: "This is a traceback string",
            close() {},
        },
    });

    await click("main button");
    await animationFrame();

    const [titleText] = queryAllTexts("main .clearfix p");
    expect(titleText).toMatch(/^Viindoo /);
    expect(titleText).not.toInclude("Odoo");
});

// A genuine unhandled server exception: the server hardcodes the raw "Odoo Server Error" as
// props.message and it recurs inside the formatted traceback, which RPCErrorDialog prefixes with
// props.data.debug. The message, the traceback and the title must all carry the Viindoo wordmark
// instead.
test("RPCErrorDialog server-error technical details never carry the raw Odoo wordmark", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(RPCErrorDialog, {
        env,
        props: {
            type: "server",
            message: "Odoo Server Error",
            name: "RPC_ERROR",
            traceback: "RPC_ERROR: Odoo Server Error",
            data: {
                debug:
                    'Traceback (most recent call last):\n  File "odoo/http.py", line 2616, ' +
                    "in handle_error\nSomeServerException: boom",
            },
            close() {},
        },
    });

    await click("main button");
    await animationFrame();

    const [titleText, messageText] = queryAllTexts("main .clearfix p");
    const tracebackText = queryText("div.o_error_detail pre");

    expect(titleText).toBe("Viindoo Server Error");
    expect(titleText).not.toInclude("Odoo");

    expect(messageText).not.toInclude("Odoo");
    expect(messageText).toInclude("Viindoo");

    expect(tracebackText).not.toInclude("Odoo");
    expect(tracebackText).toInclude("Viindoo");
});

// Core falls back to the title "Odoo Warning" when a warning carries no title of its own.
test("WarningDialog without a title of its own is headed with the Viindoo wordmark", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(WarningDialog, {
        env,
        props: { message: "Something to know", close() {} },
    });

    expect("header .modal-title").toHaveText("Viindoo Warning");
});

test("RedirectWarningDialog without a sub type is headed with the Viindoo wordmark", async () => {
    mockService("action", { doAction() {} });
    const env = await makeDialogMockEnv();
    await mountWithCleanup(RedirectWarningDialog, {
        env,
        props: {
            data: { arguments: ["Something to know", "some_action_id", "Go there"] },
            close() {},
        },
    });

    expect("header .modal-title").toHaveText("Viindoo Warning");
});

// The client error service writes two sentences naming the product into the traceback.
test("ClientErrorDialog traceback names Viindoo in the sentences of the client error service", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(ClientErrorDialog, {
        env,
        props: {
            message: "Something bad happened",
            name: "ERROR_NAME",
            traceback:
                "An error whose details cannot be accessed by the Odoo framework has occurred.\n" +
                "An unknown error occured. This may be due to a Chrome extension meddling with Odoo.",
            close() {},
        },
    });

    await click("main button");
    await animationFrame();

    const tracebackText = queryText("div.o_error_detail pre");
    expect(tracebackText).toInclude("by the Viindoo framework");
    expect(tracebackText).toInclude("meddling with Viindoo");
    expect(tracebackText).not.toInclude("Odoo");
});
