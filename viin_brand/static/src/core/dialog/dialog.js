import { Dialog } from "@web/core/dialog/dialog";

// A dialog opened without an explicit `title` shows the Viindoo wordmark, never the stock one.
// The value is a shared static: it is rewritten only when it still holds the core string, and
// reported when core changed its shape.
const coreTitle = Dialog.defaultProps?.title;
if (typeof coreTitle === "string" && coreTitle.includes("Odoo")) {
    Dialog.defaultProps.title = coreTitle.replaceAll("Odoo", "Viindoo");
} else {
    // console.error rather than console.warn: the browser test runner fails a run on an error.
    // Not a throw: a factory error would abort the rest of the bundle over a branding fallback.
    console.error(
        "viin_brand: the default Dialog title was not de-branded, expected a string containing " +
            `"Odoo" but found ${typeof coreTitle} "${String(coreTitle)}".`
    );
}
