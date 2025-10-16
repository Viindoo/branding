import { patch } from "@web/core/utils/patch";
import { SaleActionHelper } from "@sale/js/sale_action_helper/sale_action_helper";
import { SaleActionHelperDialog } from "@sale/js/sale_action_helper/sale_action_helper_dialog";


patch(SaleActionHelper.prototype, {
    openVideoPreview() {
        const viindooUrl = "https://www.youtube.com/embed/5hJ5_pMsRU4?autoplay=1";
        this.dialogService.add(SaleActionHelperDialog, 
            { url: viindooUrl }
        );
    },
});
