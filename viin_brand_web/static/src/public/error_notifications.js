import "@web/public/error_notifications";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

// The public website registers its expired session notification with the product name in its
// title and message. The terms below are the ones of the backend dialog, so the module
// translations cover them in every language.
const notifications = registry.category("error_notifications");
for (const key of ["odoo.http.SessionExpiredException", "werkzeug.exceptions.Forbidden"]) {
    const notification = notifications.get(key);
    notifications.add(
        key,
        {
            ...notification,
            title: _t("Viindoo Session Expired"),
            message: _t("Your Viindoo session expired. The current page is about to be refreshed."),
        },
        { force: true }
    );
}
