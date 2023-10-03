/** @odoo-module **/

import {NavBar} from "@web/webclient/navbar/navbar";
import {useBus, useService} from "@web/core/utils/hooks";
import {patch} from "web.utils";

const {useEffect, useRef} = owl;

// Patch Navbar to add proper icon for apps
patch(NavBar.prototype, "web_responsive.navbar", {
    setup() {
        this._super();
        this.appsMenuService = useService("apps_menu");
        this.homeMenuButton = useRef("homeMenuButton");
        useBus(this.env.bus, "TOGGLE_HOME_MENU_BUTTON", ({detail: toggle}) => {
            this.homeMenuButton.el.classList.toggle('d-none', toggle);
        });
        useEffect(() => {
            if (!this.appsMenuService.isOpening()) {
                this.env.bus.trigger('TOGGLE_HOME_MENU_BUTTON', false);
            }
        })
    },
});
