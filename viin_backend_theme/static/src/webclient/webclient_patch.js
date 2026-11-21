/** @odoo-module **/

// v19 `WebClient.loadRouterState()` calls `_loadDefaultApp()` whenever no action is resolved from the
// URL, and the same method backs the "WEBCLIENT:LOAD_DEFAULT_APP" bus event. The stock implementation
// selects the first root app; this patch lands on the flat "Applications" home menu instead.
//
// The boot landing is the only user of VIIN_HOME_ACTION: with no action resolved from the URL there
// is no controller to preserve, so the client action is used instead of the overlay the navbar apps
// icon opens (apps_menu_home.js).

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { VIIN_HOME_ACTION } from "./apps_menu_home";

patch(WebClient.prototype, {
    _loadDefaultApp() {
        // Divert only when the client action is registered: a test environment that mounts the
        // WebClient against a cleaned-out action registry would otherwise throw in doAction() on an
        // unknown tag during boot, whereas super() lands on the stock first root app.
        if (!registry.category("actions").contains(VIIN_HOME_ACTION)) {
            return super._loadDefaultApp();
        }
        return this.actionService.doAction(VIIN_HOME_ACTION);
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
