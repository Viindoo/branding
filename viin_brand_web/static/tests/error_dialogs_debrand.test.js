import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { click, queryAllTexts, queryText } from "@odoo/hoot-dom";
import { makeDialogMockEnv, mountWithCleanup } from "@web/../tests/web_test_helpers";

// Core error/crash dialog family (web/static/src/core/errors/error_dialogs.js, 19.0):
//   ErrorDialog.title           = _t("Odoo Error")
//   ClientErrorDialog.title     = _t("Odoo Client Error")   (ClientErrorDialog extends ErrorDialog {})
//   NetworkErrorDialog.title    = _t("Odoo Network Error")  (NetworkErrorDialog extends ErrorDialog {})
//   RPCErrorDialog.inferTitle() sets this.title = _t("Odoo Server Error"/"Odoo Client Error"/
//                                "Odoo Network Error") keyed on props.type ("server"/"script"/"network")
// viin_brand_common/static/src/core/errors/error_dialogs.js patches all of the above to drop the
// "Odoo" wordmark. Per owner decision D3 (MASTER_DESIGN_DOC rb633-accept-20260808-k4x9-scenarios.md,
// S13/S14/S16), the WHOLE error/crash-dialog family must read "System ..." - matching the sibling
// that is already correct (error_dialogs.js:15 `ErrorDialog.title = _t("System Error")`) and
// viin_brand_web's Dialog/ActionDialog default title, also unified on "System" by the same D3.
import { ClientErrorDialog, NetworkErrorDialog, RPCErrorDialog } from "@web/core/errors/error_dialogs";
// Side-effect import of the REAL, unmodified viin_brand_common patch so its static-field
// reassignments (lines 15-17) and the RPCErrorDialog.prototype.inferTitle patch() (lines 20-27) run
// before any test body executes (same idiom as colors_debrand.test.js / documentation_link_debrand
// .test.js / user_menu_debrand.test.js). error_dialogs.js/.xml are wired eagerly into
// web.assets_backend (__manifest__.py), so Hoot's ModuleSetLoader.setup() runs this factory before
// this test file's own module runs (see user_menu_debrand.test.js header for the full mechanism) -
// no re-import of a "patched result" is required, mounting the classes imported above already
// observes the patch.
import "@viin_brand_web/core/errors/error_dialogs";

describe.current.tags("desktop");

// Mount pattern (env + mountWithCleanup + click "main button" to reveal .o_error_detail, then read
// "main .clearfix p" / "div.o_error_detail pre") is lifted verbatim from core's OWN suite -
// addons/web/static/tests/core/errors/error_dialogs.test.js ("ErrorDialog with traceback", "Client
// ErrorDialog with traceback") - a proven pattern in this exact "desktop" tag (full services incl.
// localization, so _t()-derived TranslatedStrings resolve without needing allowTranslations(), the
// remedy the "headless" tag would otherwise require - see user_menu_debrand.test.js header).
//
// Read verbatim from core's web.ErrorDialog QWeb template (web/static/src/core/errors/
// error_dialogs.xml, 19.0), the technical-details panel:
//   <button ... t-on-click="() => { state.showTraceback = !state.showTraceback }" .../>  <- "main button"
//   <div t-if="state.showTraceback" class="... clearfix ... o_error_detail">
//     <p class="m-0"><b t-esc="title or this.constructor.title"/></p>                     <- texts[0]
//     <code t-if="props.name" t-esc="props.name"/>
//     <p class="m-0" t-if="props.message" t-esc="props.message"/>                         <- texts[1]
//     <p class="m-0" t-if="contextDetails" t-esc="contextDetails"/>                        <- texts[2]
//     <pre class="m-0 p-0 mt-2" t-esc="traceback or props.traceback"/>
//   </div>
// The dialog's OWN header (".modal-title") always reads the hardcoded "Oops!" regardless of class -
// the brand wordmark under test here lives ONLY in this technical-details panel, which stays
// collapsed (o_error_detail has count 0) until "See technical details" is clicked - exactly
// mirroring live-acceptance BUG S13-1's own repro step 4 / BUG S14-1's own repro step 3.

// BUG S13-1 (rb633-accept-20260808-k4x9 acceptance report): live-reproduced on ClientErrorDialog -
// clicking "See technical details" on a genuine client-side crash shows the bold technical-details
// title as bare "Client Error", never "System Client Error". Same class of bug flagged (not
// independently live-reproduced there) for NetworkErrorDialog - closed statically below.
//
// RED today: viin_brand_common/static/src/core/errors/error_dialogs.js:16 sets
// `ClientErrorDialog.title = _t("Client Error")` - it DROPS "Odoo" instead of PREFIXING "System",
// unlike the correct sibling on line 15 (`ErrorDialog.title = _t("System Error")`). So texts[0]
// below reads "Client Error" today, which fails `toMatch(/^System /)`.
test("ClientErrorDialog technical-details title carries the System wordmark, never bare", async () => {
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
    expect(titleText).toMatch(/^System /);
    expect(titleText).not.toInclude("Odoo");
});

// Same root cause, NetworkErrorDialog leg: error_dialogs.js:17 sets `NetworkErrorDialog.title =
// _t("Network Error")` - same missing-prefix bug, flagged in BUG S13-1 as "same class of bug" but
// not independently live-reproduced there. RED today for the same reason as above: texts[0] reads
// "Network Error", which fails `toMatch(/^System /)`.
test("NetworkErrorDialog technical-details title carries the System wordmark, never bare", async () => {
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
    expect(titleText).toMatch(/^System /);
    expect(titleText).not.toInclude("Odoo");
});

// BUG S14-1: live-reproduced on a genuine unhandled server exception - the SERVER error dialog's
// title correctly reads "System Server Error" (RPCErrorDialog.prototype.inferTitle() is already
// patched, error_dialogs.js:20-27), but the body still shows raw "Odoo Server Error" TWICE: once as
// props.message (core odoo/http.py Dispatcher.handle_error() hardcodes 'message': "Odoo Server
// Error" for ANY unhandled exception - never overridden by any viin_brand_* module, confirmed no
// Python override exists for it), and again inside the traceback (core web/static/src/core/errors/
// error_utils.js formatTraceback() prefixes "<errorName>: <error.message>" onto the traceback before
// error_handlers.js passes it as the `traceback` prop; RPCErrorDialog.setup() then prepends
// props.data.debug in front of it, so the substring survives untouched into `this.traceback`).
//
// message/traceback below mirror that exact composition: `data.debug` stands in for the Python-side
// debug traceback http.py sends over the wire, `traceback` stands in for error_utils.js's own
// formatted string - ending in "...: Odoo Server Error", exactly the tail the live report quotes:
// "caused the following client error: RPC_ERROR: Odoo Server Error".
//
// RED today: no `setup()` override exists yet in the patch() block (error_dialogs.js:20-27 patches
// ONLY inferTitle, not setup) - props.message and this.traceback both reach the template unmodified,
// so messageText/tracebackText below both still contain "Odoo" and do NOT contain "System".
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

    // Title leg: already correct today - locked in as a control so a future regression here fails
    // loudly alongside the message/traceback fix, not silently.
    expect(titleText).toBe("System Server Error");
    expect(titleText).not.toInclude("Odoo");

    // Message leg: RED today - core's raw "Odoo Server Error" is rendered verbatim.
    expect(messageText).not.toInclude("Odoo");
    expect(messageText).toInclude("System");

    // Traceback leg: RED today - the same raw string recurs inside the formatted traceback.
    expect(tracebackText).not.toInclude("Odoo");
    expect(tracebackText).toInclude("System");
});
