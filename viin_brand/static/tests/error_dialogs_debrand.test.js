import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { click, queryAllTexts, queryText } from "@odoo/hoot-dom";
import { assignDialogTestEnv, mockService, mountWithCleanup } from "@web/../tests/web_test_helpers";

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
// the context details and the traceback, and stays collapsed (a `details` element) until its
// summary is clicked. The dialog header always reads "Oops!", so the wordmark under test lives in the panel.

// A genuine client-side crash shows the bold technical-details title with the Viindoo wordmark.
test("ClientErrorDialog technical-details title carries the Viindoo wordmark, never bare", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(ClientErrorDialog, {
        props: {
            message: "Something bad happened",
            name: "ERROR_NAME",
            traceback: "This is a traceback string",
            close() {},
        },
    });

    expect("main details").not.toHaveAttribute("open");
    await click("main summary");
    await animationFrame();
    expect("main details").toHaveAttribute("open");

    const [titleText] = queryAllTexts("main .clearfix p");
    expect(titleText).toMatch(/^Viindoo /);
    expect(titleText).not.toInclude("Odoo");
});

// The details show the message of the error, as the error carries it.
test("ClientErrorDialog technical details show the message of the error", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(ClientErrorDialog, {
        props: {
            message: "Something bad happened",
            name: "ERROR_NAME",
            traceback: "This is a traceback string",
            close() {},
        },
    });

    await click("main summary");
    await animationFrame();

    expect("main .o_error_detail code.d-block").toHaveText("Something bad happened");
});

// Same rule for the NetworkErrorDialog.
test("NetworkErrorDialog technical-details title carries the Viindoo wordmark, never bare", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(NetworkErrorDialog, {
        props: {
            message: "Could not reach the server",
            name: "ERROR_NAME",
            traceback: "This is a traceback string",
            close() {},
        },
    });

    await click("main summary");
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
    assignDialogTestEnv();
    await mountWithCleanup(RPCErrorDialog, {
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

    await click("main summary");
    await animationFrame();

    const titleText = queryText("main .o_error_detail p b");
    const messageText = queryText("main .o_error_detail code.d-block");
    const tracebackText = queryText("div.o_error_detail pre");

    expect(titleText).toMatch(/Viindoo/);
    expect(titleText).not.toInclude("Odoo");

    expect(messageText).not.toInclude("Odoo");
    expect(messageText).toInclude("Viindoo");

    expect(tracebackText).not.toInclude("Odoo");
    expect(tracebackText).toInclude("Viindoo");
});

// Core falls back to the title "Odoo Warning" when a warning carries no title of its own.
test("WarningDialog without a title of its own is headed with the Viindoo wordmark", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(WarningDialog, {
        props: { message: "Something to know", close() {} },
    });

    expect(queryText("header .modal-title")).toMatch(/Viindoo/);
    expect(queryText("header .modal-title")).not.toInclude("Odoo");
});

test("RedirectWarningDialog without a sub type is headed with the Viindoo wordmark", async () => {
    mockService("action", { doAction() {} });
    assignDialogTestEnv();
    await mountWithCleanup(RedirectWarningDialog, {
        props: {
            data: { arguments: ["Something to know", "some_action_id", "Go there"] },
            close() {},
        },
    });

    expect(queryText("header .modal-title")).toMatch(/Viindoo/);
    expect(queryText("header .modal-title")).not.toInclude("Odoo");
});

// The client error service writes two sentences naming the product into the traceback.
test("ClientErrorDialog traceback names Viindoo in the sentences of the client error service", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(ClientErrorDialog, {
        props: {
            message: "Something bad happened",
            name: "ERROR_NAME",
            traceback:
                "An error whose details cannot be accessed by the Odoo framework has occurred.\n" +
                "An unknown error occured. This may be due to a Chrome extension meddling with Odoo.",
            close() {},
        },
    });

    await click("main summary");
    await animationFrame();

    const tracebackText = queryText("div.o_error_detail pre");
    expect(tracebackText).toMatch(/Viindoo/);
    expect(tracebackText).not.toInclude("Odoo");
});
