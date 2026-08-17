/** @odoo-module **/

// The navbar apps icon opens the flat home menu WITHOUT leaving the page (owner decision D3,
// 2026-08-17). Relocated out of the deleted navbar_rail.* so it survives the removal of the desktop
// rail + the mobile bottom-nav: this icon is the SOLE application switcher on every form factor.
//
// ================================================================================================
// WHAT CHANGED AND WHY - read this before touching openHomeMenu().
// ================================================================================================
// CORE'S CONTRACT FOR THIS BUTTON IS "OPEN A LIST, DO NOT NAVIGATE". `.o_navbar_apps_menu`'s trigger
// is a core <Dropdown> toggle: it opens a popover and leaves the current controller mounted.
// `web_tour/static/src/tour_utils.js:36-43` turns that into `stepUtils.showAppsMenuItem()`, and
// **57 core tour files** are built on it in two shapes:
//   1. click the apps button, then click `a[data-menu-xmlid="<app>"]` to open an app;
//   2. click the apps button as HARMLESS BOILERPLATE and keep working on the SAME view.
//
// THIS THEME USED TO BREAK BOTH. openHomeMenu() ran `actionService.doAction(VIIN_HOME_ACTION)` - a
// full-page client action, and a doAction UNMOUNTS the controller underneath. Shape 1 failed because
// the tiles were <button>s, not `a[data-menu-xmlid]`; shape 2 failed because the view the next step
// needed no longer existed. Both were observed on runbot batch 223955:
//   base.tests.test_ir_model TestIrModelFieldsTranslation.test_ir_model_fields_translation
//     -> `[2/5] ... Element (a[data-menu-xmlid="base.menu_administration"]) has not been found`
//   test_base_automation BaseAutomationTestUi.test_01_base_automation_tour / .._on_tag_added
//     -> `[2/N] ... .o_control_panel button.o-kanban-button-new`, with a screenshot showing the
//        browser sitting on the "Good morning, Administrator" home grid instead of the kanban.
//
// THE FIX IS THE MECHANISM, NOT THE LOOK. The button now opens the SAME ViinHomeMenu through the
// OVERLAY service - rendered above the still-mounted controller - and the tiles are `<a href>`
// (home_menu.xml). ONE button, ONE full-screen home menu, and the 2026-08-03 toggle round trip
// intact; the user cannot tell the two mechanisms apart, except that returning is now instant
// because the view was never torn down.
//
// WHY NOT SIMPLY KEEP CORE'S <Dropdown> AND SWAP ITS CONTENT SLOT (the obvious candidate). It was
// evaluated and rejected on THREE counts, each of which would have cost the product something:
//   * the panel would be a popover positioned by `usePosition`, which writes inline `top`/`left`;
//     making it full-screen means `!important`-ing over the framework's own inline geometry on every
//     upgrade - and this cluster's charter is explicitly no-!important-wars;
//   * `Dropdown` runs `useNavigation` over `.o-navigable` items and registers ArrowUp/ArrowDown/
//     Enter/Home/End hotkeys while open (dropdown.js), which would fight the home menu's OWN
//     arrow-key grid navigation driven from its search input - two keyboard models on one surface;
//   * the popover carries `role="menu"`, whose children must be `menuitem`s - so the app tiles would
//     have to give up their own `link` role to sit in it, and be announced as menu items that a
//     screen-reader user cannot reach through links navigation. That is an accessibility regression
//     on a change whose justification is partly accessibility, and it is exactly the defect we had
//     to remove from the tiles themselves (home_menu.xml).
//     (`bottomSheet` would also silently turn the panel into a bottom sheet on touch devices.)
// The one thing that design bought for free - dismiss-on-outside-interaction with no backdrop - is
// eight lines in home_menu.js, copied from what the Dropdown itself does.
//
// THE BOOT LANDING STAYS A CLIENT ACTION, AND THAT IS NOT A SECOND CONTROL. `WebClient._loadDefaultApp`
// (webclient_patch.js) lands on VIIN_HOME_ACTION when the URL resolves no action; there is no
// controller to preserve at boot, and an overlay over an empty action manager would be a worse
// answer. The user still sees ONE button and ONE home menu either way, so the owner's standing
// constraint - no duplicated control - is untouched. Clicking the apps icon while that landing IS
// the current controller therefore stays exactly what it has been since 2026-08-03: hand back to the
// controller underneath, or stay put when there is none.
//
// The button's `t-on-click="() => this.openHomeMenu()"` resolves `this` to the core NavBar component,
// because web.NavBar.AppsMenu is rendered via `<t t-call="web.NavBar.AppsMenu">` INSIDE web.NavBar
// (core navbar.xml), so patching NavBar.prototype is all that is needed.

import { onWillUnmount } from "@odoo/owl";
import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ControllerNotFoundError } from "@web/webclient/actions/action_service";
import { ViinHomeMenu } from "../home_menu/home_menu";

// Home-menu client action tag (D3). Still exported and still registered: it backs the BOOT LANDING
// (webclient_patch.js) and nothing else.
export const VIIN_HOME_ACTION = "viin_home_menu";

const APPS_BUTTON_SELECTOR = ".o_navbar_apps_menu .o_viin_apps_home";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.viinOverlayService = useService("overlay");
        // The overlay service's own `remove()` closure while the home menu is open; null otherwise.
        // It IS the open/closed state - there is no second flag to drift out of sync with it.
        this.viinHomeOverlay = null;
        // A navbar that is destroyed with the panel up (a reload, a fullscreen action) must not
        // strand it in the overlay container.
        onWillUnmount(() => this.closeViinHomeOverlay());
    },

    /**
     * The apps icon TOGGLES (owner request 2026-08-03: "bấm app icon lần nữa thì nó lại về lại view
     * cũ"). One control both leaves and returns.
     */
    openHomeMenu() {
        if (this.viinHomeOverlay) {
            return this.closeViinHomeOverlay({ restoreFocus: true });
        }
        // BOOT-LANDING EDGE CASE: the home menu is already the whole page. Opening an identical
        // overlay on top of it would be a visible no-op at best; hand back to the controller
        // underneath instead, or stay put when the landing is alone on the stack. Unchanged
        // behaviour, and it is what keeps core's app-switch tours green when they start at /odoo -
        // they click this button and their next step must still resolve a[data-menu-xmlid].
        if (this.isHomeMenuDisplayed()) {
            return this.closeHomeMenu();
        }
        this.viinHomeOverlay = this.viinOverlayService.add(
            ViinHomeMenu,
            {
                // A deliberate open focuses the search box; the boot landing does not, so the
                // skip-link keeps the first-Tab position (WCAG 2.4.1).
                autofocusSearch: true,
                close: (options) => this.closeViinHomeOverlay(options),
            },
            { onRemove: () => (this.viinHomeOverlay = null) }
        );
    },

    /**
     * Take the non-navigating home-menu overlay back down.
     *
     * `restoreFocus` is opt-in on purpose. Returning focus to the trigger is required when the user
     * dismissed the panel deliberately (a second click on the icon, or Escape) - WCAG 2.4.3, and it
     * is what core's Dropdown does via `focusToggleOnClosed`. It is WRONG on a dismissal caused by
     * interacting with something else: the element the user just reached for owns the focus, and
     * yanking it back to the navbar would fight them.
     *
     * @param {{restoreFocus?: boolean}} [options]
     */
    closeViinHomeOverlay({ restoreFocus = false } = {}) {
        const remove = this.viinHomeOverlay;
        this.viinHomeOverlay = null;
        remove?.();
        if (restoreFocus) {
            document.querySelector(APPS_BUTTON_SELECTOR)?.focus();
        }
    },

    /**
     * Is the flat home menu the CLIENT ACTION currently displayed? (The overlay is tracked by
     * `viinHomeOverlay`, not here - this asks only about the boot landing.)
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
     * ONLY REACHABLE FROM THE BOOT LANDING NOW. Since the navbar arm became an overlay, nothing
     * pushes a home-menu controller onto the stack any more - so in practice this either finds
     * nothing below (fresh boot: stay put) or unwinds a landing the user navigated back to.
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
     * EDGE CASES.
     *  - Fresh boot landing leaves the home menu ALONE on the stack, so there is nothing to go back
     *    to: restore() raises ControllerNotFoundError and we stay put.
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
