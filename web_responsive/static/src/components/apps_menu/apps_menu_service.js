/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Mutex} from "@web/core/utils/concurrency";
import {useService} from "@web/core/utils/hooks";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {AppsMenu, AppsMenuSearchBar} from "./apps_menu.esm.js";
import {Component, useEffect} from "@odoo/owl";


export async function nextTick() {
    await new Promise((resolve) => window.requestAnimationFrame(resolve));
    await new Promise((resolve) => setTimeout(resolve));
}

export const appsMenuService = {
    dependencies: ["action"],
    start(env) {
        let isOpening = false;
        class AppsMenuAction extends Component {
            setup() {
                this.menuService = useService("menu");
                useEffect(() => {
                    isOpening = true;
                    this.env.bus.trigger("APPS_MENU:TOGGLE", true);
                    document.body.classList.add('o_apps_menu_opened');
                    // first open
                    this.env.bus.trigger('TOGGLE_HOME_MENU_BUTTON', this.env.config.breadcrumbs.length === 1);
                    return () => {
                        isOpening = false;
                        document.body.classList.remove('o_apps_menu_opened');
                        this.env.bus.trigger("APPS_MENU:TOGGLE", false);
                    }
                }, () => []);
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

            getWebIconData(menu) {
                let result = "/web_responsive/static/img/default_icon_app.png";
                if (menu.webIconData) {
                    const prefix = menu.webIconData.startsWith("P")
                        ? "data:image/svg+xml;base64,"
                        : "data:image/png;base64,";
                    result = menu.webIconData.startsWith("data:image")
                        ? menu.webIconData
                        : prefix + menu.webIconData.replace(/\s/g, "");
                }
                return result;
            }
        }

        AppsMenuAction.components = {AppsMenu, AppsMenuSearchBar, DropdownItem};
        AppsMenuAction.target = "current";
        AppsMenuAction.template = 'web_responsive.AppsMenuAction';

        registry.category("actions").add("apps_menu", AppsMenuAction);

        return {
            isOpening() {
                return isOpening;
            },
            toggleMenu(openState) {
                return new Mutex().exec(async () => {
                    try {
                        if (openState || !isOpening) {
                            await env.services.action.doAction("apps_menu");
                        } else {
                            await env.services.action.restore();
                        }
                    } catch(e) {
                        throw e;
                    }
                    return nextTick();
                });
            },
        };
    },
};

registry.category("services").add("apps_menu", appsMenuService);
