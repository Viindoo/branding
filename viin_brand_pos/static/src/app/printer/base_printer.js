/** @odoo-module */
import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(BasePrinter.prototype, {
    /**
     * Replace the core wording, which sends the cashier to Odoo's documentation.
     * @override
     */
    getResultsError(_printResult) {
        return {
            successful: false,
            message: {
                title: _t("Connection to the printer failed"),
                body: _t(
                    "Please check if the printer is still connected. \n" +
                        "Some browsers don't allow HTTP calls from websites to devices in the network (for security reasons). " +
                        "If this is the case, ask your administrator to set up a self-signed certificate for the ePOS printer " +
                        "and a secure connection (HTTPS) between the Point of Sale and the printer. "
                ),
            },
        };
    },
});
