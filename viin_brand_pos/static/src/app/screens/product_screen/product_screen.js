import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// Plain constant, not a literal _t(): looked up in core's catalog, not copied into ours.
export const CORE_SCAN_AUTHORIZATION = "Odoo needs your authorization first.";

/** Swap core's camera-permission sentence (built inside onMounted, nothing to override). */
export function withNeutralScanError(error) {
    const coreMessage = _t(CORE_SCAN_AUTHORIZATION).toString();
    if (!(error instanceof Error) || !error.message.includes(coreMessage)) {
        return error;
    }
    return new Error(
        error.message.replace(coreMessage, _t("The system needs your authorization first."))
    );
}

patch(ProductScreen.prototype, {
    get barcodeVideoScannerProps() {
        const props = super.barcodeVideoScannerProps;
        const onError = props.onError;
        return { ...props, onError: (error) => onError(withNeutralScanError(error)) };
    },
});
