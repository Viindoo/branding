import { _t } from "@web/core/l10n/translation";
import { NotificationPlugin } from "@web/core/notifications/notification_plugin";
import { patch } from "@web/core/utils/patch";

// Plain constant, not a literal _t(): looked up in core's catalog, not copied into ours.
const CORE_WORKERS_MESSAGE =
    "You need to start Odoo with at least two workers to print a pdf version of the reports.";

// The report download names the product in the notification it raises when the server runs without
// workers; the sentence is built inside core's private message table, so it is swapped on its way
// to the notification.
function withViindooWorkersMessage(message) {
    if (String(message) === _t(CORE_WORKERS_MESSAGE).toString()) {
        return _t(
            "You need to start Viindoo with at least two workers to print a pdf version of the reports."
        );
    }
    return message;
}

patch(NotificationPlugin.prototype, {
    add(message, options) {
        return super.add(withViindooWorkersMessage(message), options);
    },
});
