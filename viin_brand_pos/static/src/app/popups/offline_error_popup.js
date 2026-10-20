// Side-effect import: a forced registry entry added before core's own makes core's add() throw.
import "@point_of_sale/app/utils/error_handlers";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ConnectionLostError } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// Mirrors "pos-offlineErrorHandler" of point_of_sale/static/src/app/utils/error_handlers.js, with
// neutral wording.
function offlineErrorHandlerOverride(env, error, originalError) {
    const candidateError = originalError || error;
    const isOfflineFetchTypeError =
        candidateError instanceof TypeError &&
        /NetworkError when attempting to fetch resource/i.test(candidateError.message || "");

    if (isOfflineFetchTypeError) {
        return true;
    }

    if (originalError instanceof ConnectionLostError) {
        const network = env.services.pos?.data?.network;
        if (!network) {
            return true;
        }
        if (!network.warningTriggered) {
            env.services.dialog.add(AlertDialog, {
                title: _t("Connection Lost"),
                body: _t(
                    "Meanwhile connection is back, Viindoo Point of Sale will operate limited operations. Check your connection or continue with limited functionalities"
                ),
                confirmLabel: _t("Continue with limited functionality"),
            });
            network.warningTriggered = true;
        }

        return true;
    }
}

registry
    .category("error_handlers")
    .add("pos-offlineErrorHandler", offlineErrorHandlerOverride, { force: true });
