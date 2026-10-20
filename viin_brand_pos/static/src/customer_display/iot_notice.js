import { _t } from "@web/core/l10n/translation";

// Plain constant, not a literal _t(): looked up in core's catalog, not copied into ours.
export const CORE_IOT_DISPLAY_ERROR =
    "Make sure there is an IoT Box subscription associated with your Odoo database, then restart the IoT Box.";

/** Return `notification` with core's IoT failure notice (names an Odoo subscription) swapped. */
export function withNeutralIotNotice(notification) {
    const coreMessage = _t(CORE_IOT_DISPLAY_ERROR);
    const wrapped = Object.create(notification);
    wrapped.add = (message, options) =>
        notification.add(
            message === coreMessage
                ? _t(
                      "Make sure the IoT Box is switched on and connected to the network, then restart the IoT Box."
                  )
                : message,
            options
        );
    return wrapped;
}
