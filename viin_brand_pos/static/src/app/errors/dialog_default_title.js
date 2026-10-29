import { Dialog } from "@web/core/dialog/dialog";

// viin_brand_web de-brands this in the backend only (its dialog.js needs the backend-only
// ActionDialog). Core's default title is the literal "Odoo".
const coreTitle = Dialog.defaultProps?.title;
if (typeof coreTitle === "string" && coreTitle.includes("Odoo")) {
    Dialog.defaultProps.title = coreTitle.replaceAll("Odoo", "Viindoo");
}
