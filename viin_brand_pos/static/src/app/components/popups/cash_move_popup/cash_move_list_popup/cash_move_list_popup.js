import { CashMoveListPopup } from "@point_of_sale/app/components/popups/cash_move_popup/cash_move_list_popup/cash_move_list_popup";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// Mirrors CashMoveListPopup.onDeleteCm of point_of_sale with a neutral error title.
patch(CashMoveListPopup.prototype, {
    async onDeleteCm(cm) {
        try {
            await this.pos.data.call(
                "pos.session",
                "delete_cash_in_out",
                [[this.pos.session.id], cm.id, this.props.partnerId],
                {},
                true
            );
            this.props.cashMoves = this.props.cashMoves.filter((cashMove) => cashMove.id !== cm.id);
        } catch (error) {
            this.dialog.add(AlertDialog, {
                title: _t("Server Error"),
                body: error.data.message,
            });
            throw error;
        }
    },
});
