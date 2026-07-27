/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
// Load-bearing import, not decoration: naming this module as a dependency makes the loader
// guarantee its factory - and therefore its `{ ...Dialog.defaultProps }` snapshot - has already
// run before we rewrite anything (web/static/src/module_loader.js:143-151, :210-215).
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// De-brand the default backend Dialog title: a dialog opened without an explicit `title` prop
// must fall back to the Viindoo wordmark, never the stock Odoo one.
//
// Core ships that fallback as a plain string literal in a static class field:
//     static defaultProps = { ... title: "Odoo" ... }
// -> odoo/addons/web/static/src/core/dialog/dialog.js:68 (19.0)
//
// Rewriting the base class alone is NOT enough. ActionDialog copies the defaults into its own
// object at class-definition time (action_dialog.js:17-20), and OWL applies
// `component.constructor.defaultProps` at render (web/static/lib/owl/owl.js:2600) - so it keeps
// whatever the base held while `web`'s assets ran, and `web` is always ordered before ours by the
// topological asset sort (odoo/addons/base/models/ir_asset.py:306). That snapshot is reachable:
// an act_window with target="new" and no `name` never sets a title prop
// (web/static/src/webclient/actions/action_service.js:1069-1071). So each snapshot is rewritten.
//
// We mutate shared statics at import time, so we assert the precondition instead of assuming it.
// Core could turn a value into something we cannot safely rewrite (a lazy `_t(...)` object, a
// getter, or nothing at all); blindly calling a string method on it would throw an opaque
// TypeError from deep inside the asset bundle, and silently skipping would ship un-debranded UI.
// We do neither: we rewrite only what we can prove is rewritable, and report the rest.
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
        // Literal wordmark substitution rather than a regex: the precondition above already
        // guarantees the shape, so a regex buys nothing and only invites a future loosening
        // (e.g. /odoo/gi) that would mangle unrelated substrings. Substituting the wordmark -
        // rather than assigning "Viindoo" outright - keeps the de-brand working if core ever
        // qualifies the literal (e.g. "Odoo 20").
        defaultProps.title = coreTitle.replaceAll(ODOO_WORDMARK, VIINDOO_WORDMARK);
    } else {
        // console.error is the project's loud channel here: Odoo's browser test runner turns any
        // console.error into a ChromeBrowserException with a screenshot (odoo/tests/common.py:1732),
        // so this fails every tour/HttpCase run - while console.warn would only be logged
        // (common.py:1817 _TO_LEVEL) and slip past CI. We deliberately do NOT throw: the module
        // loader re-raises a factory error out of odoo.define() (module_loader.js:227), which would
        // abort the rest of the backend bundle and brick the webclient over a branding fallback.
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
