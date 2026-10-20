import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { rpcErrorHandler as webRpcErrorHandler } from "@web/core/errors/error_handlers";
import { registry } from "@web/core/registry";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { CashMoveListPopup } from "@point_of_sale/app/components/popups/cash_move_popup/cash_move_list_popup/cash_move_list_popup";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import "@point_of_sale/app/utils/error_handlers";
import "@viin_brand_pos/app/popups/rpc_error_popup";
import "@viin_brand_pos/app/popups/offline_error_popup";
import "@viin_brand_pos/app/utils/order_payment_validation";
import "@viin_brand_pos/app/components/popups/cash_move_popup/cash_move_list_popup/cash_move_list_popup";
import {
    CORE_IOT_DISPLAY_ERROR,
    withNeutralIotNotice,
} from "@viin_brand_pos/customer_display/iot_notice";

describe.current.tags("headless");

beforeEach(() => {
    allowTranslations();
});

const errorHandlers = () => registry.category("error_handlers");

function makeRpcError(message = "Something failed") {
    const error = new RPCError(message);
    // not in odooExceptionTitleMap: takes the generic-title branch
    error.exceptionName = "odoo.exceptions.SomeUnmappedError";
    error.data = { message, debug: "traceback" };
    return error;
}

function makeDialogSpy() {
    const calls = [];
    return { calls, add: (Component, props) => calls.push({ Component, props }) };
}

test("a server error in the POS shows a dialog whose title does not name Odoo", () => {
    const dialog = makeDialogSpy();
    const handler = errorHandlers().get("pos-rpcErrorHandler");
    const error = makeRpcError();

    expect(handler({ services: { dialog } }, error, error)).toBe(true);

    expect(dialog.calls).toHaveLength(1);
    expect(dialog.calls[0].Component).toBe(AlertDialog);
    expect(String(dialog.calls[0].props.title)).not.toInclude("Odoo");
    expect(dialog.calls[0].props.title).not.toBe("");
    expect(dialog.calls[0].props.body).toBe("Something failed");
});

test("the POS server error handler runs before the web client's global one", () => {
    const keys = errorHandlers()
        .getEntries()
        .map(([key]) => key);
    // the global key must exist, or the order check below is vacuous
    expect(keys).toInclude("rpcErrorHandler");
    expect(keys.indexOf("pos-rpcErrorHandler")).toBeLessThan(keys.indexOf("rpcErrorHandler"));
});

test("the web client's own server error handler is not replaced", () => {
    expect(errorHandlers().get("rpcErrorHandler")).toBe(webRpcErrorHandler);
});

test("the offline notice of the POS is overridden under core's own registry key", () => {
    const dialog = makeDialogSpy();
    const network = {};
    const handler = errorHandlers().get("pos-offlineErrorHandler");
    const error = new ConnectionLostError("/some/url");

    expect(handler({ services: { dialog, pos: { data: { network } } } }, error, error)).toBe(true);

    expect(dialog.calls).toHaveLength(1);
    expect(dialog.calls[0].props.body.toString()).not.toInclude("Odoo");
    expect(network.warningTriggered).toBe(true);
    // an override under a stale key would be a dead extra entry
    expect(errorHandlers().contains("offlineErrorHandler")).toBe(false);
});

test("the offline notice is shown once per outage", () => {
    const dialog = makeDialogSpy();
    const env = { services: { dialog, pos: { data: { network: { warningTriggered: true } } } } };
    const error = new ConnectionLostError();

    expect(errorHandlers().get("pos-offlineErrorHandler")(env, error, error)).toBe(true);

    expect(dialog.calls).toHaveLength(0);
});

test("a server error while validating a payment shows a title that does not name Odoo", () => {
    const dialog = makeDialogSpy();
    const validation = { order: { state: "paid" }, pos: { dialog } };
    const error = makeRpcError();

    OrderPaymentValidation.prototype.handleValidationError.call(validation, error);

    expect(validation.order.state).toBe("draft");
    expect(dialog.calls).toHaveLength(1);
    expect(String(dialog.calls[0].props.title)).not.toInclude("Odoo");
});

test("a failed cash move deletion shows a title that does not name Odoo", async () => {
    const dialog = makeDialogSpy();
    const error = makeRpcError("Not allowed");
    const popup = {
        dialog,
        pos: {
            session: { id: 1 },
            data: {
                call: async () => {
                    throw error;
                },
            },
        },
        props: { partnerId: 7, cashMoves: [{ id: 3 }] },
    };

    let thrown;
    try {
        await CashMoveListPopup.prototype.onDeleteCm.call(popup, { id: 3 });
    } catch (e) {
        thrown = e;
    }

    expect(thrown).toBe(error);
    expect(dialog.calls).toHaveLength(1);
    expect(String(dialog.calls[0].props.title)).not.toInclude("Odoo");
    expect(dialog.calls[0].props.body).toBe("Not allowed");
});

// Core's customer display service is not in the POS unit bundle: only the wrapper is tested here.
test("the IoT customer display failure notice does not name an Odoo subscription", () => {
    const notifications = [];
    const notification = withNeutralIotNotice({
        add: (message, options) => notifications.push({ message: String(message), options }),
    });

    notification.add(_t(CORE_IOT_DISPLAY_ERROR), {
        title: "IoT Customer Display Error",
        type: "danger",
    });

    expect(notifications).toHaveLength(1);
    expect(notifications[0].message).not.toInclude("Odoo");
    expect(notifications[0].message).not.toBe(String(_t(CORE_IOT_DISPLAY_ERROR)));
    // options pass through untouched
    expect(notifications[0].options).toEqual({
        title: "IoT Customer Display Error",
        type: "danger",
    });
});

test("other notifications pass through the IoT notice wrapper unchanged", () => {
    const notifications = [];
    const notification = withNeutralIotNotice({
        add: (message, options) => notifications.push({ message, options }),
    });

    notification.add("Something else mentioning Odoo", { type: "info" });

    expect(notifications).toEqual([
        { message: "Something else mentioning Odoo", options: { type: "info" } },
    ]);
});
