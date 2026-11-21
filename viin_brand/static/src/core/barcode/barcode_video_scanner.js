import { BarcodeVideoScanner } from "@web/core/barcode/barcode_video_scanner";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// Plain constant, not a literal _t(): looked up in core's catalog, not copied into ours.
const CORE_AUTHORIZATION_MESSAGE = "Odoo needs your authorization first.";

function withViindooAuthorization(error) {
    const coreMessage = _t(CORE_AUTHORIZATION_MESSAGE).toString();
    if (!(error instanceof Error) || !error.message.includes(coreMessage)) {
        return error;
    }
    return new Error(
        error.message.replace(coreMessage, _t("Viindoo needs your authorization first.").toString())
    );
}

function withViindooErrors(props) {
    const onError = props.onError;
    return { ...props, onError: (error) => onError(withViindooAuthorization(error)) };
}

// The camera-permission sentence is built inside an `onMounted` callback that reads
// `this.props.onError` when the permission is refused, so every consumer of the scanner (the
// barcode dialog, the point of sale screens) receives the error through `props`.
patch(BarcodeVideoScanner.prototype, {
    setup() {
        super.setup();
        let props = withViindooErrors(this.props);
        Object.defineProperty(this, "props", {
            configurable: true,
            enumerable: true,
            get: () => props,
            set: (value) => {
                props = withViindooErrors(value);
            },
        });
    },
});
