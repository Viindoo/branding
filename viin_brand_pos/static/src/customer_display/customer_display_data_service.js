/** @odoo-module */
import { CustomerDisplayDataService } from "@point_of_sale/customer_display/customer_display_data_service";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

// Core's own wording, kept as a plain constant (not a literal _t() call) so it is looked up
// in core's catalog but never copied into this module's one.
const CORE_IOT_DISPLAY_ERROR =
    "Make sure there is an IoT Box subscription associated with your Odoo database, then restart the IoT Box.";

// Core shows the failure notice of the IoT-connected screen from inside start(), and it names
// an Odoo subscription. Swap that one message on the notification service start() is handed
// instead of re-implementing the service. Looked up through _t() like core does, the match
// holds in every language.
patch(CustomerDisplayDataService, {
    start(env, deps) {
        const coreMessage = _t(CORE_IOT_DISPLAY_ERROR);
        const notification = Object.create(deps.notification);
        notification.add = (message, options) =>
            deps.notification.add(
                message === coreMessage
                    ? _t(
                          "Make sure the IoT Box is switched on and connected to the network, then restart the IoT Box."
                      )
                    : message,
                options
            );
        return super.start(env, { ...deps, notification });
    },
});
