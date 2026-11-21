import { notificationPermissionService } from "@mail/core/common/notification_permission_service";
import { patch } from "@web/core/utils/patch";

// The service words its two permission toasts with the product name and offers no hook for them,
// so it is handed a notification service that renders them with the Viindoo name.
patch(notificationPermissionService, {
    start(env, services) {
        const { notification } = services;
        return super.start(env, {
            ...services,
            notification: {
                ...notification,
                add: (message, options) =>
                    notification.add(String(message).replaceAll("Odoo", "Viindoo"), options),
            },
        });
    },
});
