import { patch } from "@web/core/utils/patch";
import { SaleActionHelper } from "@sale/js/sale_action_helper/sale_action_helper";
import { SaleActionHelperDialog } from "@sale/js/sale_action_helper/sale_action_helper_dialog";

export const VIINDOO_QUOTATION_VIDEO_URL = "https://www.youtube.com/embed/5hJ5_pMsRU4?autoplay=1";

patch(SaleActionHelper.prototype, {
    openVideoPreview() {
        this.dialogService.add(SaleActionHelperDialog, { url: VIINDOO_QUOTATION_VIDEO_URL });
    },
});
