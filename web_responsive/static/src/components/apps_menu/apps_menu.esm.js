/* global document */

/* Copyright 2018 Tecnativa - Jairo Llopis
 * Copyright 2021 ITerra - Sergey Shebanin
 * Copyright 2023 Onestein - Anjeel Haria
 * Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { Component, useState, useRef } from "@odoo/owl";
import { useBus, useService } from "@web/core/utils/hooks";
import {AppMenuItem} from "@web_responsive/components/apps_menu_item/apps_menu_item.esm";
import {AppsMenuSearchBar} from "@web_responsive/components/menu_searchbar/searchbar.esm";
import {NavBar} from "@web/webclient/navbar/navbar";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";
import {router} from "@web/core/browser/router";
import {session} from "@web/session";
import {useHotkey} from "@web/core/hotkeys/hotkey_hook";
import {BurgerMenu} from "@web/webclient/burger_menu/burger_menu";


export class AppsMenu extends Component {
    static template = "web_responsive.AppsMenu";
    static props = {
        // AppsMenu is only ever instantiated as a child of AppsMenuScreen (apps_menu.xml's
        // "web_responsive.AppsMenuAction" template), which itself only exists while the menu is
        // actually being presented - so the caller always knows the right value up front. Reading
        // it as a prop, instead of starting closed and waiting for AppsMenuScreen's mounted-effect
        // to correct it one render cycle later over the APPS_MENU:TOGGLE bus, is what makes
        // `.app-menu-container` (t-if="state.open", apps_menu.xml:52) appear in the SAME render
        // cycle as `.o_grid_apps_menu` instead of a frame later - closing the ~20ms empty-overlay
        // flash a mocked single-frame click (and, on a slow device, a real one) could otherwise
        // observe.
        open: {type: Boolean, optional: true},
        slots: {
            type: Object,
            optional: true,
        },
    };
    setup() {
        super.setup();
        this.state = useState({open: this.props.open ?? false});
        this.theme = session.apps_menu?.theme || "milk";
        this.menuService = useService("menu");
        browser.localStorage.setItem("redirect_menuId", "");
        if (session.apps_menu?.is_redirect_home) {
            this.router = router;
            const menuId = Number(this.router.current.menu_id || 0);
            this.state = useState({open: menuId === 0});
        }
        this.actionService = useService("action");
        this.homeIcon = useRef("homeIcon");
        useBus(this.env.bus, "APPS_MENU:TOGGLE", ({ detail: open }) => {
            this.setOpenState(open);
        });
        this._setupKeyNavigation();
    }

    setOpenState(open_state) {
        this.state.open = open_state;
    }

    /**
     * Setup navigation among app menus
     */
    _setupKeyNavigation() {
        const repeatable = {
            allowRepeat: true,
        };
        useHotkey(
            "ArrowRight",
            () => {
                this._onWindowKeydown("next");
            },
            repeatable
        );
        useHotkey(
            "ArrowLeft",
            () => {
                this._onWindowKeydown("prev");
            },
            repeatable
        );
        useHotkey(
            "ArrowDown",
            () => {
                this._onWindowKeydown("next");
            },
            repeatable
        );
        useHotkey(
            "ArrowUp",
            () => {
                this._onWindowKeydown("prev");
            },
            repeatable
        );
        useHotkey("Escape", () => {
            this.env.bus.trigger("ACTION_MANAGER:UI-UPDATED");
        });
    }

    _onWindowKeydown(direction) {
        const focusableInputElements = document.querySelectorAll(".o-app-menu-item");
        if (focusableInputElements.length) {
            const focusable = [...focusableInputElements];
            const index = focusable.indexOf(document.activeElement);
            let nextIndex = 0;
            if (direction === "prev" && index >= 0) {
                if (index > 0) {
                    nextIndex = index - 1;
                } else {
                    nextIndex = focusable.length - 1;
                }
            } else if (direction === "next") {
                if (index + 1 < focusable.length) {
                    nextIndex = index + 1;
                } else {
                    nextIndex = 0;
                }
            }
            focusableInputElements[nextIndex].focus();
        }
    }

}

// Add this patch after the WebClient patch
patch(NavBar.prototype, {
    setup() {
        super.setup();

        useBus(this.env.bus, "APP_MENU:TOGGLE_SIDEBAR", () => {
            this._openAppMenuSidebar();
        });
    },

    openAppMenu() {
        this.env.bus.trigger("APP_MENU:OPEN_APP_MENU");
        this._closeAppMenuSidebar();
    },
});

Object.assign(NavBar.components, {AppsMenu, AppMenuItem, AppsMenuSearchBar});

// Add this patch after the WebClient patch
patch(BurgerMenu.prototype, {
    setup() {
        super.setup();
    },

    _openAppMenuSidebarMobile() {
        this.env.bus.trigger("APP_MENU:TOGGLE_SIDEBAR");
    },
});
