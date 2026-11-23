import { _t } from "@web/core/l10n/translation";
import {
    ErrorDialog,
    ClientErrorDialog,
    NetworkErrorDialog,
    RPCErrorDialog,
    WarningDialog,
    RedirectWarningDialog,
} from "@web/core/errors/error_dialogs";
import { patch } from "@web/core/utils/patch";

ErrorDialog.title = _t("Viindoo Error");
ClientErrorDialog.title = _t("Viindoo Client Error");
NetworkErrorDialog.title = _t("Viindoo Network Error");

// The technical details show `this.message`, which starts as the message of the error: props are
// read-only, so the product name is replaced on this copy (see error_dialogs.xml).
// The client error service writes two sentences naming the product into the technical details.
patch(ErrorDialog.prototype, {
    setup() {
        super.setup();
        this.message = this.props.message;
        if (typeof this.props.traceback === "string") {
            this.traceback = this.props.traceback
                .replace(/by the Odoo framework/g, "by the Viindoo framework")
                .replace(/meddling with Odoo/g, "meddling with Viindoo");
        }
    },
});

// The server hardcodes "Odoo Server Error" into every unhandled exception, so the wordmark is
// replaced in the title and in the technical-details body (message and traceback).
// props.data, the raw debug payload, is left untouched.
patch(RPCErrorDialog.prototype, {
    setup() {
        super.setup();
        if (this.message) {
            this.message = this.message.toString().replace(/Odoo/g, "Viindoo");
        }
        if (this.traceback) {
            this.traceback = this.traceback.toString().replace(/Odoo/g, "Viindoo");
        }
    },
    inferTitle() {
        super.inferTitle();
        if (this.title) {
            this.title = this.title.toString().replace(/Odoo/g, "Viindoo");
        }
    },
});

patch(WarningDialog.prototype, {
    inferTitle() {
        const title = super.inferTitle();
        if (String(title) === String(_t("Odoo Warning"))) {
            return _t("Viindoo Warning");
        }
        return title;
    },
});

patch(RedirectWarningDialog.prototype, {
    setup() {
        super.setup();
        if (String(this.title) === String(_t("Odoo Warning"))) {
            this.title = _t("Viindoo Warning");
        }
    },
});
