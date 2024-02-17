/** @odoo-module **/
/* Copyright 2018 Tecnativa - Jairo Llopis
 * Copyright 2021 ITerra - Sergey Shebanin
 * Copyright 2023 Onestein - Anjeel Haria
 * Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import {Component, useState, useRef} from "@odoo/owl";
import {session} from "@web/session";
import {useBus, useService} from "@web/core/utils/hooks";
import {AppMenuItem} from "@web_responsive/components/apps_menu_item/apps_menu_item.esm";
import {AppsMenuSearchBar} from "@web_responsive/components/menu_searchbar/searchbar.esm";
import {NavBar} from "@web/webclient/navbar/navbar";
import {useHotkey} from "@web/core/hotkeys/hotkey_hook";


export class AppsMenu extends Component {
    setup() {
        super.setup();
        this.state = useState({open: false});
        this.theme = session.apps_menu.theme || "milk";
        this.menuService = useService("menu");
        this.actionService = useService("action");
        this.homeIcon = useRef("homeIcon");
        useBus(this.env.bus, "APPS_MENU:TOGGLE", ({detail: open}) => {
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

Object.assign(AppsMenu, {
    template: "web_responsive.AppsMenu",
    props: {
        slots: {
            type: Object,
            optional: true,
        },
    },
});

Object.assign(NavBar.components, {AppsMenu, AppMenuItem, AppsMenuSearchBar});
