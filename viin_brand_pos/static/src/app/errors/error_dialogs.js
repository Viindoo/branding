import { ErrorDialog } from "@web/core/errors/error_dialogs";
import { patch } from "@web/core/utils/patch";

// Core's error service puts two English sentences naming the product in the technical details;
// the template prints `traceback or props.traceback`, so they are scrubbed there.
const NAMING_CORE_SENTENCES = [
    [/by the Odoo framework/g, "by the system"],
    [/meddling with Odoo/g, "meddling with the system"],
];

export function scrubBrandFromTraceback(traceback) {
    return NAMING_CORE_SENTENCES.reduce(
        (text, [pattern, replacement]) => text.replace(pattern, replacement),
        traceback
    );
}

patch(ErrorDialog.prototype, {
    setup() {
        super.setup();
        if (typeof this.props.traceback === "string") {
            this.traceback = scrubBrandFromTraceback(this.props.traceback);
        }
    },
});
