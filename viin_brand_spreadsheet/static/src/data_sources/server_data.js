import { BatchEndpoint } from "@spreadsheet/data_sources/server_data";
import { patch } from "@web/core/utils/patch";

// The message of a formula whose data failed to load sends the user to the support site of the
// product vendor.
patch(BatchEndpoint.prototype, {
    _handleBatchFailure(batch) {
        const results = super._handleBatchFailure(batch);
        for (const error of results.values()) {
            error.message = error.message.replaceAll("odoo.com/help", "viindoo.com/ticket");
        }
        return results;
    },
});
