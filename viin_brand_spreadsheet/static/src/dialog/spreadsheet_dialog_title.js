import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { DialogPlugin } from "@web/core/dialog/dialog_plugin";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// The spreadsheet confirmation and error dialogs are titled "Odoo Spreadsheet" by a hook that is
// not patchable, so that one title is re-worded when the dialog is opened; every other dialog
// keeps the title it was opened with.
patch(DialogPlugin.prototype, {
    add(dialogClass, props, options) {
        if (
            dialogClass === ConfirmationDialog &&
            props?.title &&
            String(props.title) === String(_t("Odoo Spreadsheet"))
        ) {
            props = { ...props, title: String(props.title).replaceAll("Odoo", "Viindoo") };
        }
        return super.add(dialogClass, props, options);
    },
});
