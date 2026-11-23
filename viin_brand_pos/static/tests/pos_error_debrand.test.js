import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { Component, signal, xml } from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
import { rpcErrorHandler as webRpcErrorHandler } from "@web/core/errors/error_handlers";
import { registry } from "@web/core/registry";
import {
    allowTranslations,
    getService,
    mountWithCleanup,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { setupPosEnvWithoutScale } from "@viin_brand_pos/../tests/pos_test_env";
import { definePosModels } from "@point_of_sale/../tests/unit/data/generate_model_definitions";
import { CashMoveListPopup } from "@point_of_sale/app/components/popups/cash_move_popup/cash_move_list_popup/cash_move_list_popup";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import "@point_of_sale/app/utils/error_handlers";
import "@viin_brand_pos/app/popups/rpc_error_popup";
import "@viin_brand_pos/app/popups/offline_error_popup";
import "@viin_brand_pos/app/utils/order_payment_validation";
import "@viin_brand_pos/app/components/popups/cash_move_popup/cash_move_list_popup/cash_move_list_popup";

definePosModels();

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

/** Record the dialogs the POS opens instead of rendering them. */
function recordDialogs() {
    const calls = [];
    patchWithCleanup(getService("dialog"), {
        add: (Component, props) => calls.push({ Component, props }),
    });
    return calls;
}

/** Run a registered error handler as the error service does: in the scope of a component. */
async function runErrorHandler(name, error) {
    let handled;
    class Probe extends Component {
        static template = xml`<div/>`;
        setup() {
            handled = errorHandlers().get(name)(this.env, error, error);
        }
    }
    await mountWithCleanup(Probe);
    return handled;
}

test("a server error in the POS shows a dialog whose title does not name Odoo", async () => {
    await setupPosEnvWithoutScale();
    const dialogs = recordDialogs();
    const error = makeRpcError();

    expect(await runErrorHandler("pos-rpcErrorHandler", error)).toBe(true);

    expect(dialogs).toHaveLength(1);
    expect(dialogs[0].Component).toBe(AlertDialog);
    expect(String(dialogs[0].props.title)).not.toInclude("Odoo");
    expect(String(dialogs[0].props.title)).toInclude("Viindoo");
    expect(dialogs[0].props.body).toBe("Something failed");
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

test("the offline notice of the POS is overridden under core's own registry key", async () => {
    const store = await setupPosEnvWithoutScale();
    const dialogs = recordDialogs();
    store.data.network.warningTriggered = false;
    const error = new ConnectionLostError("/some/url");

    expect(await runErrorHandler("pos-offlineErrorHandler", error)).toBe(true);

    expect(dialogs).toHaveLength(1);
    expect(dialogs[0].props.body.toString()).not.toInclude("Odoo");
    expect(store.data.network.warningTriggered).toBe(true);
    // an override under a stale key would be a dead extra entry
    expect(errorHandlers().contains("offlineErrorHandler")).toBe(false);
});

test("the offline notice is shown once per outage", async () => {
    const store = await setupPosEnvWithoutScale();
    const dialogs = recordDialogs();
    store.data.network.warningTriggered = true;
    const error = new ConnectionLostError();

    expect(await runErrorHandler("pos-offlineErrorHandler", error)).toBe(true);

    expect(dialogs).toHaveLength(0);
});

test("a server error while validating a payment shows a title that does not name Odoo", () => {
    const calls = [];
    const validation = {
        order: { state: "paid" },
        pos: { dialog: { add: (Component, props) => calls.push({ Component, props }) } },
    };
    const error = makeRpcError();

    OrderPaymentValidation.prototype.handleValidationError.call(validation, error);

    expect(validation.order.state).toBe("draft");
    expect(calls).toHaveLength(1);
    expect(String(calls[0].props.title)).not.toInclude("Odoo");
    expect(String(calls[0].props.title)).toInclude("Viindoo");
});

function makeCashMovePopup({ call, onDelete = () => {} }) {
    const calls = [];
    return {
        calls,
        popup: {
            dialog: { add: (Component, props) => calls.push({ Component, props }) },
            pos: { session: { id: 1 }, data: { call } },
            props: { partnerId: 7, onDelete },
            cashMoves: signal([{ id: 3 }, { id: 4 }]),
        },
    };
}

test("a failed cash move deletion shows a title that does not name Odoo", async () => {
    const error = makeRpcError("Not allowed");
    const { popup, calls } = makeCashMovePopup({
        call: async () => {
            throw error;
        },
    });

    let thrown;
    try {
        await CashMoveListPopup.prototype.onDeleteCm.call(popup, { id: 3 });
    } catch (e) {
        thrown = e;
    }

    expect(thrown).toBe(error);
    expect(calls).toHaveLength(1);
    expect(String(calls[0].props.title)).not.toInclude("Odoo");
    expect(String(calls[0].props.title)).toInclude("Viindoo");
    expect(calls[0].props.body).toBe("Not allowed");
    expect(popup.cashMoves().map((cashMove) => cashMove.id)).toEqual([3, 4]);
});

test("a deleted cash move leaves the list and the parent is told", async () => {
    const deleted = [];
    const { popup, calls } = makeCashMovePopup({
        call: async () => true,
        onDelete: (id) => deleted.push(id),
    });

    await CashMoveListPopup.prototype.onDeleteCm.call(popup, { id: 3 });

    expect(popup.cashMoves().map((cashMove) => cashMove.id)).toEqual([4]);
    expect(deleted).toEqual([3]);
    expect(calls).toHaveLength(0);
});
