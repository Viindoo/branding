/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import {
    ClientErrorDialog,
    ErrorDialog,
    NetworkErrorDialog,
    odooExceptionTitleMap,
    RedirectWarningDialog,
    RPCErrorDialog,
    WarningDialog,
} from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// ActionDialog copies Dialog.defaultProps when core defines it, so it keeps "Odoo" unless it is
// branded itself. Importing it also guarantees it is defined before this file brands it.
for (const component of [Dialog, ActionDialog]) {
    component.defaultProps.title = component.defaultProps.title.replace(/Odoo/g, "Viindoo");
}

// Error and warning dialogs build their titles from translated "Odoo ..." terms, so the brand is
// replaced by new terms of this module, which the module translations cover in every language.
ErrorDialog.title = _t("Viindoo Error");
ClientErrorDialog.title = _t("Viindoo Client Error");
NetworkErrorDialog.title = _t("Viindoo Network Error");

patch(RPCErrorDialog.prototype, {
    inferTitle() {
        super.inferTitle(...arguments);
        // Only the fallbacks by error type carry the product name; a title taken from the
        // exception name map (Validation Error, Access Denied...) has none.
        if (odooExceptionTitleMap.has(this.props.exceptionName)) {
            return;
        }
        switch (this.props.type) {
            case "server":
                this.title = _t("Viindoo Server Error");
                break;
            case "script":
                this.title = _t("Viindoo Client Error");
                break;
            case "network":
                this.title = _t("Viindoo Network Error");
                break;
        }
    },
});

patch(WarningDialog.prototype, {
    inferTitle() {
        const title = super.inferTitle(...arguments);
        const named = odooExceptionTitleMap.has(this.props.exceptionName) || this.props.title;
        return named ? title : _t("Viindoo Warning").toString();
    },
});

patch(RedirectWarningDialog.prototype, {
    setup() {
        super.setup(...arguments);
        if (!this.props.subType) {
            this.title = _t("Viindoo Warning");
        }
    },
});
