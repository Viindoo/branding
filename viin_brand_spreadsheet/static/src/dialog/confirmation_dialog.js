import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// The spreadsheet confirmation and error dialogs are titled "Odoo Spreadsheet" through a hook that
// is not patchable, so that one title is re-worded when the dialog is built; every other dialog
// keeps the title it was opened with.
patch(ConfirmationDialog.prototype, {
    setup() {
        super.setup();
        if (String(this.props.title) === String(_t("Odoo Spreadsheet"))) {
            this.props.title = String(this.props.title).replaceAll("Odoo", "Viindoo");
        }
    },
});
