/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { SaleFileUploadListRenderer } from "@sale/views/sale_file_upload_list/sale_file_upload_list_renderer";
import { patch } from "@web/core/utils/patch";

patch(SaleFileUploadListRenderer.prototype, {
    setup() {
        super.setup();
        this.dropZoneDescription = _t(`
            If your customer runs on version 18 or higher, customer data and sales order lines
            will be automatically created. Any other pdf containing an attached
            UBL-RequestForQuotation file will work as well.
        `);
    },
});
