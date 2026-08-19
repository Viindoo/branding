/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Mutex } from "@web/core/utils/concurrency";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { useService } from "@web/core/utils/hooks";
import { AppsMenu } from "./apps_menu.esm.js";
import { AppMenuItem } from "@web_responsive/components/apps_menu_item/apps_menu_item.esm";
import { AppsMenuSearchBar } from "@web_responsive/components/menu_searchbar/searchbar.esm";
import { Component, useEffect } from "@odoo/owl";

export async function nextTick() {
    await new Promise((resolve) => window.requestAnimationFrame(resolve));
    await new Promise((resolve) => setTimeout(resolve));
}

/**
 * The Home Menu screen: the app grid plus its search bar.
 *
 * Presented two ways, which is why the screen itself is a base class rather than the client
 * action it used to be:
 *
 *  - AppsMenuAction  - the client action still registered under the "menu" tag, which is what
 *    the /odoo URL and core's breadcrumb special-case (action_service.js: _getBreadcrumbs keeps
 *    only controllers whose action.tag !== "menu") resolve to. It is also the PATCH TARGET
 *    third-party modules reach for by class name (see the comment on its own declaration below).
 *  - AppsMenuOverlay - how a user actually opens it. Rendered through the "overlay" service, ON
 *    TOP of whatever the user was already looking at, so their view is never unmounted. It
 *    extends AppsMenuAction below, not this base class directly, so a prototype patch() applied
 *    to AppsMenuAction is inherited here too - both presentations must carry the same prototype
 *    surface for a third-party patch to reach whichever one actually renders for the user.
 *
 * Everything observable about the screen - the o_apps_menu_opened body class, the APPS_MENU:*
 * bus events, the app grid - is identical in both, so it lives here once.
 */
export class AppsMenuScreen extends Component {
    static template = "web_responsive.AppsMenuAction";
    static components = { AppsMenu, AppMenuItem, AppsMenuSearchBar };
    static props = {};
    setup() {
        this.menuService = useService("menu");
        this.appsMenu = useService("apps_menu");
        useEffect(
            () => {
                this.appsMenu.setOpen(true);
                this.env.bus.trigger("APPS_MENU:TOGGLE", true);
                document.body.classList.add("o_apps_menu_opened");
                // Hide the navbar's own Home button only while there is nothing behind the
                // menu to go back to - otherwise the user needs it to dismiss the menu again.
                this.env.bus.trigger("TOGGLE_HOME_MENU_BUTTON", this.coversNothing);
                return () => {
                    document.body.classList.remove("o_apps_menu_opened");
                    this.env.bus.trigger("TOGGLE_HOME_MENU_BUTTON", false);
                    this.appsMenu.setOpen(false);
                    // Must match the open-side trigger three lines up and AppsMenu's own listener
                    // (apps_menu.esm.js: useBus(this.env.bus, "APPS_MENU:TOGGLE", ...)). This used
                    // to fire "APPS_MENU:ACT:TOGGLE" - a name with no listener at all since the
                    // dual-event open/close design (both "ACT:TOGGLE" and "TOGGLE" fired together)
                    // was consolidated onto "APPS_MENU:TOGGLE" alone; the close side was never
                    // updated to match. Harmless today only because the whole subtree is destroyed
                    // by this same cleanup anyway, but a silently-unheard close event is exactly the
                    // kind of asymmetry that bites the next thing that listens for it.
                    this.env.bus.trigger("APPS_MENU:TOGGLE", false);
                };
            },
            () => [],
        );
    }

    /**
     * True when the menu is the only thing on screen. As an overlay there is no breadcrumb
     * trail to read, so the question is whether the action service holds a controller at all -
     * which is exactly the boot case (_loadDefaultApp opening straight into the Home Menu).
     */
    get coversNothing() {
        return !this.env.services.action.currentController;
    }

    get apps() {
        return this.menuService.getApps();
    }

    get currentApp() {
        return this.menuService.getCurrentApp();
    }

    /**
     * Dismiss the screen. The client action is dismissed by the action stack itself; the
     * overlay has to be removed explicitly.
     */
    dismiss() {}

    onNavBarDropdownItemSelection(menu) {
        if (menu) {
            // Picking an app must put the user in that app, not leave the menu covering it.
            this.dismiss();
            this.menuService.selectMenu(menu);
        }
    }

    getMenuItemHref(payload) {
        const parts = [`menu_id=${payload.id}`];
        if (payload.actionID) {
            parts.push(`action=${payload.actionID}`);
        }
        return "#" + parts.join("&");
    }
}

/**
 * The class registered under the "menu" actions tag - and the PATCH TARGET third-party modules
 * reach for by class name (e.g. erponline-enterprise/viin_customizer_web_responsive's
 * `patch(AppsMenuAction.prototype, {...})`), which also extends this screen's shared template
 * ("web_responsive.AppsMenuAction") by name. Any other presentation of this screen (AppsMenuOverlay
 * below is the only one today) MUST descend from this class rather than sit beside it as a sibling
 * of AppsMenuScreen - a sibling renders the same template without the patched prototype members,
 * which is exactly the regression this fix repairs: `TypeError: ctx.getAppCreatorItem is not a
 * function` on the overlay once a third party had patched only AppsMenuAction.
 */
export class AppsMenuAction extends AppsMenuScreen {
    static props = { ...standardActionServiceProps };
    static displayName = _t("Home");
    static target = "current";

    get coversNothing() {
        return !this.env.config.breadcrumbs.length;
    }
}

registry.category("actions").add("menu", AppsMenuAction);

/**
 * How the user actually opens the Home Menu (see appsMenuService.openMenu below) - rendered
 * through the "overlay" service ON TOP of whatever they were already looking at. Deliberately a
 * DESCENDANT of AppsMenuAction, not a sibling of it, so a patch() applied to AppsMenuAction's
 * prototype - by this module or a third party, in either load order - is inherited here too.
 * `static target` / `static displayName` are inherited from AppsMenuAction but inert for an
 * overlay (it is never pushed onto the action stack) - left as-is on purpose, not "cleaned up".
 */
export class AppsMenuOverlay extends AppsMenuAction {
    static props = { close: { type: Function } };

    // AppsMenuAction's override reads env.config.breadcrumbs, which only a mounted action
    // controller has; an overlay has none, so resolve it the way the base class does instead.
    get coversNothing() {
        return !this.env.services.action.currentController;
    }

    dismiss() {
        this.props.close();
    }
}

export const appsMenuService = {
    dependencies: ["action", "overlay"],
    start(env) {
        let isOpening = false;
        let removeOverlay = null;
        // One mutex for the service, not one per call: a fresh Mutex per invocation serialises
        // nothing, which is the whole point of holding one.
        const mutex = new Mutex();

        // KNOWN TRAP, deliberately left unfixed - see toggleMenu() below for the mechanism.
        // AppsMenuScreen.setup()'s useEffect calls appsMenu.setOpen(true) unconditionally
        // (isOpening = true) on mount, regardless of WHICH presentation mounted it. That is fine
        // for the overlay presentation - openMenu() below is what set removeOverlay in the first
        // place. But this module also registers AppsMenuAction under the "menu" actions tag
        // (registry.category("actions").add("menu", ...)): if anything ever mounts that action
        // directly - doAction("menu"), a client-action URL, a third-party module - isOpening
        // becomes true WITHOUT openMenu() ever having run, so removeOverlay stays null. The next
        // click on the apps button calls toggleMenu() with no argument: `openState` is falsy and
        // `isOpening` is already true, so the `else` branch below runs closeMenu() - which checks
        // `if (removeOverlay)`, finds null, and does nothing. The button is then completely dead
        // (verified live: 3 clicks, 0 change) until the action itself is dismissed some other way.
        // Unreachable TODAY - a repo-wide grep of branding18/tvtmaaddons18/erponline-enterprise18
        // finds no doAction("menu") caller and no ir.actions.client row for it - so there is no
        // live path to red-then-green a fix against. Deciding what closeMenu() SHOULD do when the
        // action presentation (not the overlay) is what's mounted - synthesize an overlay-shaped
        // teardown? dismiss the action instead? - needs its own design and its own reachable test,
        // not a guess bolted onto this bug's fix. Left as a documented trap for whoever gives a
        // third-party module a reason to reach this tag directly.
        const closeMenu = () => {
            if (removeOverlay) {
                removeOverlay();
                removeOverlay = null;
            }
        };

        const openMenu = () => {
            if (removeOverlay) {
                return;
            }
            // An overlay is rendered above the action manager and never touches the controller
            // stack, so the view the user was on stays mounted underneath and needs no refetch
            // when the menu is dismissed. Opening the Home Menu as an action with
            // target="current" instead REPLACED that view and destroyed it.
            removeOverlay = env.services.overlay.add(AppsMenuOverlay, { close: closeMenu });
        };

        return {
            setOpen(value) {
                isOpening = !!value;
            },
            isOpening() {
                return isOpening;
            },
            toggleMenu(openState) {
                return mutex.exec(async () => {
                    if (openState || !isOpening) {
                        openMenu();
                    } else {
                        closeMenu();
                    }
                    return nextTick();
                });
            },
        };
    },
};

registry.category("services").add("apps_menu", appsMenuService);
