/** @odoo-module **/

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

// Patch static titles - use generic "System" instead of brand name
ErrorDialog.title = _t("System Error");
ClientErrorDialog.title = _t("System Client Error");
NetworkErrorDialog.title = _t("System Network Error");

// Patch RPCErrorDialog.inferTitle to remove "Odoo" branding, and setup() to
// scrub the same wordmark from the technical-details body (props.message and
// the component's own traceback field) - the raw "Odoo Server Error" string
// core's Dispatcher.handle_error() hardcodes into every unhandled server
// exception. props.data (the raw debug payload) is left untouched.
patch(RPCErrorDialog.prototype, {
    setup() {
        super.setup();
        if (this.props.message) {
            this.props.message = this.props.message.toString().replace(/Odoo/g, "System");
        }
        if (this.traceback) {
            this.traceback = this.traceback.toString().replace(/Odoo/g, "System");
        }
    },
    inferTitle() {
        super.inferTitle();
        if (this.title) {
            this.title = this.title.toString().replace(/Odoo/g, "System");
        }
    },
});

// Patch WarningDialog.inferTitle fallback
patch(WarningDialog.prototype, {
    inferTitle() {
        const title = super.inferTitle();
        if (title === _t("Odoo Warning").toString()) {
            return _t("Warning");
        }
        return title;
    },
});

// Patch RedirectWarningDialog.setup for fallback title
patch(RedirectWarningDialog.prototype, {
    setup() {
        super.setup();
        if (this.title === _t("Odoo Warning").toString()) {
            this.title = _t("Warning");
        }
    },
});
