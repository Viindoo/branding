import { Dialog } from "@web/core/dialog/dialog";
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// ActionDialog copies `Dialog.defaultProps` when its class is defined and OWL applies
// `constructor.defaultProps` at render, so the copy needs the same de-brand as the base class.
// The copy may already hold the de-branded base title, depending on which file loads first.
const coreTitle = ActionDialog.defaultProps?.title;
if (typeof coreTitle === "string" && coreTitle.includes("Odoo")) {
    ActionDialog.defaultProps.title = coreTitle.replaceAll("Odoo", "Viindoo");
} else if (coreTitle !== Dialog.defaultProps?.title) {
    console.error(
        "viin_brand: the default ActionDialog title was not de-branded, expected a string " +
            `containing "Odoo" but found ${typeof coreTitle} "${String(coreTitle)}".`
    );
}
