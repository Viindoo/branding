/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { SaleFileUploadKanbanRenderer } from "@sale/views/sale_file_upload_kanban/sale_file_upload_kanban_renderer";
import { patch } from "@web/core/utils/patch";

patch(SaleFileUploadKanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.dropZoneDescription = _t(`
            If your customer runs on version 18 or higher, customer data and sales order lines
            will be automatically created. Any other pdf containing an attached
            UBL-RequestForQuotation file will work as well.
        `);
    },
});
