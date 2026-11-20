import { patch } from "@web/core/utils/patch";
import { iapNotificationService } from "@iap_mail/js/services/iap_notification_service";

// A service out of credits is announced with its title only: there are no credits to buy.
patch(iapNotificationService, {
    start(env, { bus_service, notification }) {
        bus_service.subscribe("iap_notification", ({ message, title, type }) => {
            notification.add(message || "", {
                title,
                type: type === "no_credit" ? "danger" : type,
            });
        });
        bus_service.start();
    },
});
