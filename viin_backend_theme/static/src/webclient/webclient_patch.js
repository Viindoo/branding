/** @odoo-module **/

// P1 - WebClient landing (TDD §4b P1; fidelity amendment 2026-07-18 M4).
//
// v19 `WebClient.loadRouterState()` calls `_loadDefaultApp()` whenever no action is resolved from the
// URL (webclient.js:137-140), and the same method backs the "WEBCLIENT:LOAD_DEFAULT_APP" bus event.
// The stock implementation selects the first root app; we override it to land on the flat
// "Applications" home menu (D3) instead. This is the CORRECT v19 hook - the amendment's M4 recorded
// that the earlier build patched a non-existent `_loadDefaultApp` on the prototype, which is exactly
// the method patched here (it DOES exist in v19).
//
// The title de-brand (setParts zopenerp: "Viindoo") is INHERITED from viin_brand_common's own
// WebClient patch and is deliberately NOT duplicated here - the two patches compose cleanly.
//
// T-4 (PR #658 review-fix): skipToMainContent backs the "Skip to main content" bypass-blocks link
// (WCAG 2.4.1) that webclient.xml prepends as the FIRST focusable element in the shell - it moves
// keyboard focus straight into the action region, past the navbar + rail chrome.

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { VIIN_HOME_ACTION } from "./apps_menu_home";

patch(WebClient.prototype, {
    _loadDefaultApp() {
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
