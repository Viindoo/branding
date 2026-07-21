/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

// Patch WebClient to show AppsMenu instead of default app
patch(WebClient.prototype, {
    setup() {
        super.setup();
        // Read apps_menu optionally so isolated core WebClient tests (which do
        // not start this service) keep working once web_responsive is installed.
        this.appsMenuService = this.env.services.apps_menu;
    },
    _loadDefaultApp() {
        // Only divert to the fullscreen menu when the "apps_menu" client
        // action is registered: core mail multi-tab QUnit envs start the
        // service but run with a cleaned actions registry, so doAction would
        // throw "Cannot find apps_menu in this registry!" and fail every
        // cross-tab test.
        if (this.appsMenuService && registry.category("actions").contains("apps_menu")) {
            return this.appsMenuService.toggleMenu(true);
        }
        return super._loadDefaultApp();
    },
});
