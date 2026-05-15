/** @odoo-module **/

import { NavBar } from "@web/webclient/navbar/navbar";
import { useBus, useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { useRef } from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.appsMenuService = useService("apps_menu");
        this.homeMenuButton = useRef("homeMenuButton");
        useBus(this.env.bus, "TOGGLE_HOME_MENU_BUTTON", ({detail: toggle}) => {
            this.homeMenuButton.el.classList.toggle('d-none', toggle);
        });
    },
});
