import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import { RPCError } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { handleRPCError } from "@viin_brand_pos/app/popups/rpc_error_popup";

// Core calls its exported handleRPCError directly (an ES import cannot be replaced).
patch(OrderPaymentValidation.prototype, {
    handleValidationError(error) {
        if (error instanceof RPCError) {
            this.order.state = "draft";
            handleRPCError(error, this.pos.dialog);
            return error;
        }
        return super.handleValidationError(...arguments);
    },
});
