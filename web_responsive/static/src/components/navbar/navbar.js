/** @odoo-module **/

import {NavBar} from "@web/webclient/navbar/navbar";
import {useBus, useService} from "@web/core/utils/hooks";
import {patch} from "web.utils";

const {useRef} = owl;

// Patch Navbar to add proper icon for apps
patch(NavBar.prototype, "web_responsive.navbar", {
    setup() {
        this._super();
        this.appsMenuService = useService("apps_menu");
        this.homeMenuButton = useRef("homeMenuButton");
        useBus(this.env.bus, "TOGGLE_HOME_MENU_BUTTON", ({detail: toggle}) => {
            this.homeMenuButton.el.classList.toggle('d-none', toggle);
        });
    },
    getWebIconData(menu) {
        var result = "/web_responsive/static/img/default_icon_app.png";
        if (menu.webIconData) {
            const prefix = menu.webIconData.startsWith("P")
                ? "data:image/svg+xml;base64,"
                : "data:image/png;base64,";
            result = menu.webIconData.startsWith("data:image")
                ? menu.webIconData
                : prefix + menu.webIconData.replace(/\s/g, "");
        }
        return result;
    },
});
