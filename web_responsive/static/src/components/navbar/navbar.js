/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { useBus } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { useRef } from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        // Read apps_menu optionally: the NavBar is mounted by isolated core
        // component tests that do not start this service, and useService() would
        // throw and break them as soon as web_responsive is installed.
        this.appsMenuService = this.env.services.apps_menu;
        this.homeMenuButton = useRef("homeMenuButton");
        useBus(this.env.bus, "TOGGLE_HOME_MENU_BUTTON", ({detail: toggle}) => {
            // `t-ref="homeMenuButton"` (apps_menu.xml) only renders on the t-else branch of
            // web.NavBar.AppsMenu's isSmall check - a small screen renders the `.o_menu_toggle`
            // anchor instead, so `this.homeMenuButton.el` is null there. That control is not
            // toggled by this event on mobile either way (it never was, before or after
            // apps_menu.xml moved the button inside `t-else`): a no-op on a null ref preserves
            // that pre-existing mobile behaviour instead of crashing the bus listener.
            this.homeMenuButton.el?.classList.toggle('d-none', toggle);
        });
    },
});
