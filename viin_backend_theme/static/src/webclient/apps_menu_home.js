/** @odoo-module **/

// Apps-menu -> flat home menu repurpose (PR #658 item 1). Relocated OUT of the deleted navbar_rail.*
// so it survives the removal of the desktop rail + the mobile bottom-nav: the navbar apps icon is now
// the SOLE application switcher on every form factor.
//
// Core app-switch TOURS (mass_mailing `mailing_campaign`, im_livechat, and every tour built on
// stepUtils.showAppsMenuItem) FIRST click `.o_navbar_apps_menu button:enabled`, so that button MUST
// stay visible + enabled - hiding it with d-none broke those tours (runbot build 223591). So the
// inner core <Dropdown> (a SECOND app list) is REPLACED by a plain button that opens the ONE flat
// home menu (ViinHomeMenu, client action "viin_home_menu") - see apps_menu_home.xml. The home-menu
// tiles expose `.o_app[data-menu-xmlid]`, exactly the selector those tours target at their next step,
// so the whole showAppsMenuItem -> `.o_app[data-menu-xmlid]` pattern still resolves.
//
// The button's `t-on-click="() => this.openHomeMenu()"` resolves `this` to the core NavBar component,
// because web.NavBar.AppsMenu is rendered via `<t t-call="web.NavBar.AppsMenu">` INSIDE web.NavBar
// (core navbar.xml), so a minimal ADDITIVE patch of openHomeMenu() on NavBar.prototype is all that is
// needed - core NavBar.setup() already assigns this.actionService (core navbar.js), so no setup()
// override is required.

import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { ControllerNotFoundError } from "@web/webclient/actions/action_service";

// Home-menu client action tag (D3). Exported here (moved from the deleted navbar_rail.js) so the boot
// landing WebClient._loadDefaultApp (webclient_patch.js) imports the constant from this surviving
// module instead of the removed rail file.
export const VIIN_HOME_ACTION = "viin_home_menu";

patch(NavBar.prototype, {
    /**
     * The apps icon TOGGLES (owner request 2026-08-03: "bấm app icon lần nữa thì nó lại về lại view
     * cũ"). Away from the home menu it opens it; ON the home menu it puts back the controller the
     * user came from, so one control both leaves and returns.
     */
    openHomeMenu() {
        if (this.isHomeMenuDisplayed()) {
            return this.closeHomeMenu();
        }
        // User-triggered open -> autofocus the home-menu search. The boot landing
        // (WebClient._loadDefaultApp) omits this flag so the skip-link keeps the first-Tab position.
        return this.actionService.doAction(VIIN_HOME_ACTION, {
            additionalContext: { viin_home_focus_search: true },
        });
    },

    /**
     * Is the flat home menu the action currently displayed?
     *
     * Reads `actionService.currentController.action.tag` and NOT `actionService.currentAction`:
     * the latter is an ASYNC getter (action_service.js:335 `async function _getCurrentAction`) that
     * hands back a Promise and, for a virtual controller, round-trips an RPC - so `.tag` on it is
     * always undefined and it cannot answer a synchronous click handler. `currentController` is the
     * plain sync getter (:324-327) over the top of the controller stack, and a client action's
     * controller carries the preprocessed action verbatim, `tag` included (:1296-1316).
     *
     * @returns {boolean}
     */
    isHomeMenuDisplayed() {
        return this.actionService.currentController?.action?.tag === VIIN_HOME_ACTION;
    },

    /**
     * Put back the controller the user came from, using the action service's OWN breadcrumb stack.
     *
     * WHY restore() AND NOT history.back(). `browser.history.back()` is a BROWSER-level undo of the
     * URL; the webclient is a single-page app whose view state lives in the action service's
     * controller stack, so a raw history step can land on a URL the stack no longer matches and
     * leave the two out of sync. `actionService.restore()` is the action manager's own re-entry
     * point: with no argument it targets the PENULTIMATE controller (action_service.js:1719-1725),
     * re-mounts it through `_updateUI` (which also rewrites the URL) and truncates the stack so the
     * home-menu entry is dropped instead of accumulating. This is verbatim the mechanism core itself
     * uses for "go back one controller" - `controller.config.historyBack` restores the penultimate
     * controller and only falls back to the default-app bus event when there is none
     * (action_service.js:914-920).
     *
     * WHY NOTHING IS REMEMBERED ACROSS THE OPEN. An earlier draft stashed the outgoing controller's
     * jsId on the component. That is state that can go stale (a second NavBar instance, a remount)
     * for no gain: opening the home menu PUSHES it on top of the stack, so "the controller below the
     * home menu" already IS "where the user came from" - no bookkeeping needed. Launching an app
     * from a tile then clears the stack anyway (menuService.selectMenu passes clearBreadcrumbs:true,
     * menu_service.js:92-97), so the pair can never accumulate.
     *
     * EDGE CASES.
     *  - Fresh boot landing (WebClient._loadDefaultApp) leaves the home menu ALONE on the stack, so
     *    there is nothing to go back to: restore() raises ControllerNotFoundError and we stay put,
     *    which is also what keeps core's app-switch tours green - they start at /odoo (already on
     *    the home menu), click the apps button, and must still find `.o_app[data-menu-xmlid]` after.
     *  - The controller below is ITSELF a home menu: loop until a different action surfaces.
     *  - restore() can legitimately do nothing when the outgoing view refuses to leave
     *    (clearUncommittedChanges returns false, action_service.js:1731-1734). The jsId guard below
     *    detects that no-op and stops, so the loop can never spin.
     */
    async closeHomeMenu() {
        let previousJsId = this.actionService.currentController?.jsId;
        while (this.isHomeMenuDisplayed()) {
            try {
                await this.actionService.restore();
            } catch (error) {
                if (error instanceof ControllerNotFoundError) {
                    return; // nothing below the home menu - stay on it
                }
                throw error;
            }
            const jsId = this.actionService.currentController?.jsId;
            if (jsId === previousJsId) {
                return; // the restore was refused (unsaved changes) - do not retry
            }
            previousJsId = jsId;
        }
    },
});
