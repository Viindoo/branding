/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { Mutex } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";
import { AppsMenu } from "./apps_menu.esm.js";
import { AppMenuItem } from "@web_responsive/components/apps_menu_item/apps_menu_item.esm";
import { AppsMenuSearchBar } from "@web_responsive/components/menu_searchbar/searchbar.esm";
import { Component, useEffect } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export async function nextTick() {
    await new Promise((resolve) => window.requestAnimationFrame(resolve));
    await new Promise((resolve) => setTimeout(resolve));
}

export class AppsMenuAction extends Component {
    static template = "web_responsive.AppsMenuAction";
    static components = { AppsMenu, AppMenuItem, AppsMenuSearchBar };
    static props = { ...standardActionServiceProps };
    static displayName = _t("Home");
    static target = "current";
    setup() {
        this.menuService = useService("menu");
        this.appsMenu = useService("apps_menu");
        useEffect(
            () => {
                this.appsMenu.setOpen(true);
                this.env.bus.trigger("APPS_MENU:TOGGLE", true);
                document.body.classList.add("o_apps_menu_opened");
                // first open
                this.env.bus.trigger(
                    "TOGGLE_HOME_MENU_BUTTON",
                    !this.env.config.breadcrumbs.length,
                );
                return () => {
                    document.body.classList.remove("o_apps_menu_opened");
                    this.env.bus.trigger("TOGGLE_HOME_MENU_BUTTON", false);
                    this.appsMenu.setOpen(false);
                    this.env.bus.trigger("APPS_MENU:ACT:TOGGLE", false);
                };
            },
            () => [],
        );
    }

    get apps() {
        return this.menuService.getApps();
    }

    get currentApp() {
        return this.menuService.getCurrentApp();
    }

    onNavBarDropdownItemSelection(menu) {
        if (menu) {
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

registry.category("actions").add("menu", AppsMenuAction);

export const appsMenuService = {
    dependencies: ["action"],
    start(env) {
        let isOpening = false;
        return {
            setOpen(value) {
                isOpening = !!value;
            },
            isOpening() {
                return isOpening;
            },
            toggleMenu(openState) {
                return new Mutex().exec(async () => {
                    try {
                        if (openState || !isOpening) {
                            await env.services.action.doAction("menu");
                        } else {
                            await env.services.action.restore();
                        }
                    } catch (e) {
                        throw e;
                    }
                    return nextTick();
                });
            },
        };
    },
};

registry.category("services").add("apps_menu", appsMenuService);
