import { CustomerDisplayDataService } from "@point_of_sale/customer_display/customer_display_data_service";
import { patch } from "@web/core/utils/patch";
import { withNeutralIotNotice } from "@viin_brand_pos/customer_display/iot_notice";

// Swap that one message on the notification service start() is handed instead of
// re-implementing the service.
patch(CustomerDisplayDataService, {
    start(env, deps) {
        return super.start(env, { ...deps, notification: withNeutralIotNotice(deps.notification) });
    },
});
