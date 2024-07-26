/** @odoo-module */

import { OfflineErrorPopup } from "@point_of_sale/app/errors/popups/offline_error_popup";
import { _t } from "@web/core/l10n/translation";


OfflineErrorPopup.defaultProps.body = _t(
    "Meanwhile connection is back, Viindoo Point of Sale will operate limited operations. Check your connection or continue with limited functionalities"
);
