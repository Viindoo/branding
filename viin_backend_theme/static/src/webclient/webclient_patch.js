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
// THE BOOT LANDING IS THE ONLY REMAINING USER OF VIIN_HOME_ACTION (owner decision D3, 2026-08-17).
// The navbar apps icon used to doAction() this same client action, which is what unmounted the
// controller underneath and broke 57 core tours; it now opens the home menu as a non-navigating
// overlay instead (apps_menu_home.js). The boot landing keeps the client action deliberately: with
// no action resolved from the URL there is no controller to preserve, and an overlay floating over
// an empty action manager would be strictly worse. The user sees ONE button and ONE home menu on
// both paths, so this is not a second control.
//
// The title de-brand is INHERITED from viin_brand_web and is deliberately NOT duplicated here.
// It no longer lives in a WebClient patch: commit 9a5083d moved it into
// viin_brand_web/static/src/core/browser/title_service.js, which de-brands the title service's
// EMPTY-composition fallback ("Odoo" -> "Viindoo") instead of injecting a permanent `zopenerp` title
// part that leaked into every composed title ("Viindoo - Hello, world!"). Behaviour here is
// unaffected either way - this file simply must not re-state where that de-brand lives.
//
// T-4 (PR #658 review-fix): skipToMainContent backs the "Skip to main content" bypass-blocks link
// (WCAG 2.4.1) that webclient.xml prepends as the FIRST focusable element in the shell - it moves
// keyboard focus straight into the action region, past the navbar + rail chrome.

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { VIIN_HOME_ACTION } from "./apps_menu_home";

patch(WebClient.prototype, {
    _loadDefaultApp() {
        // Divert to the home menu ONLY when that client action is actually registered.
        // home_menu.js registers "viin_home_menu" into registry.category("actions") at module
        // load, so in a real client the guard always passes. It matters in test environments
        // that mount the WebClient against a cleaned-out action registry: an unguarded
        // doAction() on an unknown tag throws during boot and takes the whole suite with it,
        // whereas super() lands on the stock first-root-app exactly as an unthemed build does.
        // Forward-ported intent from 18.0 web_responsive (221946b) - the module is gone at 19.0
        // but this hook carries the identical hazard, so the guard is re-expressed here.
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
