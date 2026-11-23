// Side-effect import: a forced registry entry added before core's own makes core's add() throw.
import "@point_of_sale/app/utils/error_handlers";
import { odooExceptionTitleMap, ErrorDialog } from "@web/core/errors/error_dialogs";
import { RPCError } from "@web/core/network/rpc";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// Mirrors handleRPCError of point_of_sale/static/src/app/utils/error_handlers.js, with a Viindoo title.
export function handleRPCError(error, dialog) {
    const { data } = error;
    if (odooExceptionTitleMap.has(error.exceptionName)) {
        const title = odooExceptionTitleMap.get(error.exceptionName).toString();
        dialog.add(AlertDialog, { title, body: data.message });
    } else if (odoo.debug === "assets") {
        dialog.add(ErrorDialog, {
            traceback: data.message + "\n" + data.debug + "\n",
        });
    } else {
        dialog.add(AlertDialog, {
            title: _t("Viindoo Server Error"),
            body: data.message,
        });
    }
}

function rpcErrorHandlerOverride(env, error, originalError) {
    const dialog = useService("dialog");
    if (originalError instanceof RPCError) {
        handleRPCError(originalError, dialog);
        return true;
    }
}

// The POS key, not the web client's global "rpcErrorHandler" (it runs after this one). `force` keeps
// the core sequence.
registry
    .category("error_handlers")
    .add("pos-rpcErrorHandler", rpcErrorHandlerOverride, { force: true });
