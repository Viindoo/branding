/** @odoo-module **/

import {useService} from "@web/core/utils/hooks";
import {WebClient} from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";


// Patch WebClient to show AppsMenu instead of default app
patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.appsMenuService = useService("apps_menu");
    },
    _loadDefaultApp() {
        return this.appsMenuService.toggleMenu(true);
    }
});
