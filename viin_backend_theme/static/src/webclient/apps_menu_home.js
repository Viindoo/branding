/** @odoo-module **/

// The navbar apps icon opens the flat home menu without leaving the page: it is the sole
// application switcher on every form factor.
//
// Core's contract for this button is "open a list, do not navigate": `.o_navbar_apps_menu`'s trigger
// is a core <Dropdown> toggle that leaves the current controller mounted, and core tours built on
// `stepUtils.showAppsMenuItem()` rely on it, either clicking `a[data-menu-xmlid="<app>"]` to open an
// app or clicking the button and carrying on in the same view. So openHomeMenu() renders ViinHomeMenu
// through the overlay service above the still-mounted controller, and the tiles are `<a href>`
// (home_menu.xml); a doAction() would unmount the controller underneath.
//
// Core's <Dropdown> is not reused with a swapped content slot because:
//   * the popover is positioned by `usePosition` with inline `top`/`left`, so a full-screen panel
//     would need `!important` over the framework's own geometry;
//   * `Dropdown` registers arrow/Enter/Home/End navigation over `.o-navigable` items, which would
//     fight the home menu's own arrow-key grid navigation;
//   * the popover's `role="menu"` would force the app tiles to give up their `link` role.
// Dismissal on outside interaction, without a backdrop, is what home_menu.js reimplements.
//
// The boot landing stays a client action (VIIN_HOME_ACTION, webclient_patch.js): there is no
// controller to preserve at boot. Clicking the apps icon while that landing is the current
// controller hands back to the controller underneath, or stays put when there is none.
//
// `t-on-click="() => this.openHomeMenu()"` resolves `this` to the core NavBar component, because
// web.NavBar.AppsMenu is rendered through `<t t-call>` inside web.NavBar, so patching
// NavBar.prototype is enough.

import { onWillUnmount } from "@odoo/owl";
import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useBus, useService } from "@web/core/utils/hooks";
import { routerBus } from "@web/core/browser/router";
import { ControllerNotFoundError } from "@web/webclient/actions/action_service";
import { ViinHomeMenu } from "../home_menu/home_menu";

// Home-menu client action tag; it backs the boot landing (webclient_patch.js).
export const VIIN_HOME_ACTION = "viin_home_menu";

// The control that toggles the home menu: the desktop apps button, or - on a small screen, where
// core renders `a.o_menu_toggle` instead - that anchor. Exactly one of the two exists at a time.
// (home_menu.js's APPS_MENU_SELECTOR is the matching "this pointerdown is the toggle's own" area.)
const APPS_BUTTON_SELECTOR = ".o_navbar_apps_menu .o_viin_apps_home, .o_menu_toggle";

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
        // The route changed under the panel: the handle must not outlive it, or a panel that mounts
        // late would cover the new screen. A screen that merely finishes loading (the app reloading
        // behind a panel the user just opened) is not a route change and must leave the panel up.
        useBus(routerBus, "ROUTE_CHANGE", () => this.closeViinHomeOverlay());
    },

    /**
     * Toggle the home menu: one control both opens it and, on a second click, returns.
     * `ViinHomeMenu` pre-focuses its own search box on mount, so no autofocus prop is passed.
     */
    openHomeMenu() {
        if (this.viinHomeOverlay) {
            return this.closeViinHomeOverlay({ restoreFocus: true });
        }
        // Boot landing: the home menu is already the whole page, so hand back to the controller
        // underneath (or stay put when there is none) instead of stacking an identical overlay. Core's
        // app-switch tours start at /odoo and click this button; their next step must still resolve
        // a[data-menu-xmlid].
        if (this.isHomeMenuDisplayed()) {
            return this.closeHomeMenu();
        }
        this.viinHomeOverlay = this.viinOverlayService.add(
            ViinHomeMenu,
            {
                close: (options) => this.closeViinHomeOverlay(options),
            },
            { onRemove: () => (this.viinHomeOverlay = null) }
        );
    },

    /**
     * Small screens: the toggle (`a.o_menu_toggle`, core's `_openAppMenuSidebar`) reaches the SAME
     * home menu the desktop button does, with the same "is something behind it" rule - no second
     * predicate. Gated on the home menu being involved at all, so with nothing of ours open the
     * toggle is core's sidebar toggle, untouched (also after the sidebar is already open: a second
     * tap closes it).
     *  - overlay up (a screen is behind it): put the overlay away, back to that screen, no sidebar;
     *  - boot landing up: `closeHomeMenu()` restores the screen behind it if there is one; when
     *    nothing is behind it the home menu stays and the sidebar opens over it (no blank page).
     */
    async _openAppMenuSidebar() {
        if (this.viinHomeOverlay) {
            // A handle with no panel on screen is a stale one: drop it and carry on, so the tap is
            // never swallowed by a panel nobody can see.
            const isShown = Boolean(document.querySelector(".o_viin_home_overlay"));
            this.closeViinHomeOverlay({ restoreFocus: isShown });
            if (isShown) {
                return;
            }
        }
        if (this.isHomeMenuDisplayed()) {
            await this.closeHomeMenu();
            if (!this.isHomeMenuDisplayed()) {
                return; // returned to the screen that was behind the landing
            }
        }
        return super._openAppMenuSidebar(...arguments);
    },

    /**
     * Small screens: the sidebar's "All Apps" button opens the full-screen home menu with its
     * search box instead of core's inline app list. Desktop has no sidebar and keeps core's handler.
     * When the home menu already IS the screen, or no screen has loaded yet (boot landing), there is
     * nothing to open: the sidebar just steps aside - `openHomeMenu()` would hand a displayed
     * landing back to the screen below it.
     */
    onAllAppsBtnClick() {
        if (!this.ui.isSmall) {
            return super.onAllAppsBtnClick(...arguments);
        }
        this._closeAppMenuSidebar();
        // Only over a real screen: while the boot landing is still loading there is no controller
        // yet, and a panel opened over nothing would mount late on top of whatever loads next.
        const hasScreen = Boolean(this.actionService.currentController);
        if (hasScreen && !this.viinHomeOverlay && !this.isHomeMenuDisplayed()) {
            this.openHomeMenu();
        }
    },

    /**
     * Take the home-menu overlay down. `restoreFocus` is opt-in: focus returns to the trigger after a
     * deliberate dismissal (a second click on the icon, Escape; WCAG 2.4.3), but not when the user
     * dismissed it by reaching for another element, which owns the focus.
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
     * Is the flat home menu, as the boot-landing client action, currently displayed? The overlay is
     * tracked by `viinHomeOverlay`.
     *
     * Reads the sync `actionService.currentController.action.tag`, not `currentAction`, which is an
     * async getter that returns a Promise.
     *
     * @returns {boolean}
     */
    isHomeMenuDisplayed() {
        return this.actionService.currentController?.action?.tag === VIIN_HOME_ACTION;
    },

    /**
     * Put back the controller the user came from, using the action service's own controller stack.
     * Only the boot landing reaches it: the navbar overlay never pushes a controller.
     *
     * `actionService.restore()` is used rather than `history.back()` because the view state lives in
     * the controller stack, and a raw history step can leave the URL and the stack out of sync.
     *  - A fresh boot landing is alone on the stack: restore() raises ControllerNotFoundError and the
     *    home menu stays.
     *  - When the controller below is itself a home menu, loop until a different action surfaces.
     *  - restore() does nothing when the outgoing view refuses to leave (unsaved changes); the jsId
     *    guard detects that no-op and stops the loop.
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
