/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
// Load-bearing import: it makes the loader run ActionDialog's factory, and therefore its
// `{ ...Dialog.defaultProps }` snapshot, before this module rewrites anything.
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// A dialog opened without an explicit `title` falls back to the Viindoo wordmark, never the
// stock Odoo one.
//
// Rewriting the base class alone is not enough: ActionDialog copies the defaults into its own
// object at class-definition time and OWL applies `constructor.defaultProps` at render, so that
// snapshot keeps whatever the base held while `web`'s assets ran (`web` always sorts before this
// module). The snapshot is reachable - an act_window with target="new" and no `name` never sets a
// title prop - so each snapshot is rewritten.
//
// These are shared statics mutated at import time, so the precondition is asserted instead of
// assumed: core could turn the value into something that cannot be safely rewritten (a lazy
// `_t(...)` object, a getter, nothing). Only a provably rewritable value is rewritten; the rest
// is reported loudly rather than skipped silently or thrown from inside the asset bundle.
const ODOO_WORDMARK = "Odoo";
const VIINDOO_WORDMARK = "Viindoo";

// Every class carrying its OWN default title. If core adds another class that snapshots
// Dialog.defaultProps, add it here and mirror it in static/tests/action_dialog_debrand.test.js.
const DEBRAND_TARGETS = [
    ["Dialog", Dialog],
    ["ActionDialog", ActionDialog],
];

const rewritten = new Set();

for (const [label, target] of DEBRAND_TARGETS) {
    const defaultProps = target?.defaultProps;
    if (defaultProps && rewritten.has(defaultProps)) {
        // Same object reached twice through static inheritance - a subclass that stopped
        // declaring its own defaults now resolves to the base object we just rewrote.
        continue;
    }
    if (defaultProps) {
        rewritten.add(defaultProps);
    }
    const coreTitle = defaultProps?.title;
    if (typeof coreTitle === "string" && coreTitle.includes(ODOO_WORDMARK)) {
        // A literal substitution, not a regex, and not an outright assignment: it keeps working
        // if core ever qualifies the literal (e.g. "Odoo 20") without risking a looser pattern.
        defaultProps.title = coreTitle.replaceAll(ODOO_WORDMARK, VIINDOO_WORDMARK);
    } else {
        // console.error, not console.warn: Odoo's browser test runner fails every tour/HttpCase
        // run on an error but only logs a warning. Not a throw either: a factory error aborts the
        // rest of the backend bundle and would brick the webclient over a branding fallback.
        console.error(
            `viin_brand_web: default ${label} title was NOT de-branded. Expected ` +
                `${label}.defaultProps.title to be a string containing "${ODOO_WORDMARK}" ` +
                '(Odoo 19.0 core sets the literal "Odoo" in ' +
                `web/static/src/core/dialog/dialog.js), but found type "${typeof coreTitle}" ` +
                `with value "${String(coreTitle)}". The stock value is left untouched. ` +
                "Either core changed the default (make this patch handle the new shape) or " +
                "another module already rewrote it (this patch is now dead code). " +
                "Review viin_brand_web/static/src/core/dialog/dialog.js against current core."
        );
    }
}
