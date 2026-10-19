/** @odoo-module */
import { odooExceptionTitleMap, ErrorDialog } from "@web/core/errors/error_dialogs";
import { RPCError } from "@web/core/network/rpc";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// Same behaviour as core's handler, only the generic dialog title no longer names Odoo.
function handleRPCError(error, dialog) {
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
            title: _t("Server Error"),
            body: data.message,
        });
    }
}

function rpcErrorHandlerOverride(env, error, originalError) {
    if (originalError instanceof RPCError) {
        handleRPCError(originalError, env.services.dialog);
        return true;
    }
}

registry
    .category("error_handlers")
    .add("rpcErrorHandler", rpcErrorHandlerOverride, { force: true });
