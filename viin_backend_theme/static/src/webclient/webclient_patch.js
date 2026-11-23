// `WebClient.loadRouterState()` calls `_loadDefaultApp()` whenever no action is resolved from the
// URL, and the same method backs the "WEBCLIENT:LOAD_DEFAULT_APP" bus event. The stock implementation
// selects the first root app; this patch lands on the flat "Applications" home menu instead.
//
// The boot landing is the only user of VIIN_HOME_ACTION: with no action resolved from the URL there
// is no controller to preserve, so the client action is used instead of the overlay the navbar apps
// icon opens (apps_menu_home.js).
//
// Like the stock default app (`menuService.selectMenu`), the landing clears the breadcrumbs, and the
// dialogs open when it loads are closed by `doAction`. When the view of an action fails to load, the
// landing replaces it and the error of that load reaches the error service as an unhandled rejection
// at a moment nothing orders against the landing: the landing of a failed load is the home menu
// alone, so the error handler below takes the error of that load, and only that one, instead of
// opening its dialog over the landing. Every other error opens its dialog as in core.

import { UncaughtPromiseError } from "@web/core/errors/error_service";
import { RPCError } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { VIIN_HOME_ACTION } from "./apps_menu_home";

// The model of the view that the landing replaced, from the landing of a failed load until the error
// of that load is handled or the user acts. The views that load lazily (list, kanban, graph, pivot)
// are the ones whose failed load sends the web client to its default app and rethrows the error
// afterwards, with no user input in between; the same bus event also follows a missing action, with
// no error to come, so the first input of the user ends the wait and a later error is never taken.
let failedLoadModel = null;
const USER_INPUT_EVENTS = ["pointerdown", "keydown"];

function setFailedLoadModel(model) {
    for (const type of USER_INPUT_EVENTS) {
        window.removeEventListener(type, clearFailedLoadModel, true);
    }
    failedLoadModel = model;
    if (model) {
        for (const type of USER_INPUT_EVENTS) {
            window.addEventListener(type, clearFailedLoadModel, true);
        }
    }
}

function clearFailedLoadModel() {
    setFailedLoadModel(null);
}

/**
 * Takes the error of the load that failed, which the landing of the failed load replaced: it opens no
 * dialog over the home menu. It runs before the handler of the RPC errors (sequence 97) and takes
 * one error: the first RPC error of the model of the replaced view.
 *
 * @param {OdooEnv} env
 * @param {UncaughtError} error
 * @param {Error} originalError
 * @returns {boolean}
 */
export function failedLoadLandingErrorHandler(env, error, originalError) {
    if (
        failedLoadModel === null ||
        !(error instanceof UncaughtPromiseError) ||
        !(originalError instanceof RPCError) ||
        originalError.model !== failedLoadModel
    ) {
        return false;
    }
    clearFailedLoadModel();
    error.unhandledRejectionEvent.preventDefault();
    return true;
}

registry
    .category("error_handlers")
    .add("viinFailedLoadLandingErrorHandler", failedLoadLandingErrorHandler, { sequence: 96 });

patch(WebClient.prototype, {
    _loadDefaultApp(ev) {
        // Divert only when the client action is registered: a test environment that mounts the
        // WebClient against a cleaned-out action registry would otherwise throw in doAction() on an
        // unknown tag during boot, whereas super() lands on the stock first root app.
        if (!registry.category("actions").contains(VIIN_HOME_ACTION)) {
            return super._loadDefaultApp(...arguments);
        }
        // Only the bus event, never the boot landing, can follow a failed load, and a form never
        // loads lazily: the view that the landing replaces is a lazy view with its own model.
        const replaced = ev instanceof Event ? this.actionService.currentController : null;
        const isLazyView = replaced?.props?.type && replaced.props.type !== "form";
        setFailedLoadModel((isLazyView && replaced.action?.res_model) || null);
        return this.actionService.doAction(VIIN_HOME_ACTION, { clearBreadcrumbs: true });
    },

    /** Move focus into the main action region (the skip-link target). The action manager is not
     *  natively focusable, so make it programmatically focusable first, then focus it. */
    skipToMainContent() {
        const main = document.querySelector(".o_action_manager");
        if (main) {
            main.setAttribute("tabindex", "-1");
            main.focus();
        }
    },
});
