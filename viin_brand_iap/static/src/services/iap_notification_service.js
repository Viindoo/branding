import { patch } from "@web/core/utils/patch";
import { iapNotificationService } from "@iap_mail/js/services/iap_notification_service";

// A service out of credits is announced without the button that opens the page to buy credits:
// the notification handed to core's service carries no button.
patch(iapNotificationService, {
    start(env, services) {
        const { notification } = services;
        return super.start(env, {
            ...services,
            notification: {
                add: (message, options) => notification.add(message, { ...options, buttons: [] }),
            },
        });
    },
});
