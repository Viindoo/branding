import { OutOfFocusService } from "@mail/core/common/out_of_focus_service";
import { patch } from "@web/core/utils/patch";

const CORE_ICON = "/mail/static/src/img/odoobot_transparent.webp";
const BRAND_ICON = "/viin_brand/static/img/viindoobot.png";

// A message without an author is announced with core's bot mark; it carries the Viindoo bot.
patch(OutOfFocusService.prototype, {
    sendNativeNotification(title, message, icon, options) {
        return super.sendNativeNotification(
            title,
            message,
            icon === CORE_ICON ? BRAND_ICON : icon,
            options
        );
    },
});
