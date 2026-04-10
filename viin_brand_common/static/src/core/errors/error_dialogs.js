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

// Patch static titles — use generic "System" instead of brand name
ErrorDialog.title = _t("System Error");
ClientErrorDialog.title = _t("Client Error");
NetworkErrorDialog.title = _t("Network Error");

// Patch RPCErrorDialog.inferTitle to remove "Odoo" branding
patch(RPCErrorDialog.prototype, {
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
