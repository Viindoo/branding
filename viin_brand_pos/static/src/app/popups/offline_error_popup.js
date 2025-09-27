/** @odoo-module */
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ConnectionLostError } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

function offlineErrorHandlerOverride(env, error, originalError) {
    if (originalError instanceof ConnectionLostError) {
        if (!env.services.pos.data.network.warningTriggered) {
            env.services.dialog.add(AlertDialog, {
                title: _t("Connection Lost"),
                body: _t(
                    "Meanwhile connection is back, Viindoo Point of Sale will operate limited operations. Check your connection or continue with limited functionalities"
                ),
                confirmLabel: _t("Continue with limited functionality"),
            });
            env.services.pos.data.network.warningTriggered = true;
        }

        return true;
    }
}

registry
    .category("error_handlers")
    .add("offlineErrorHandler", offlineErrorHandlerOverride, { force: true });
