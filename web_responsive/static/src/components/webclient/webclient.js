/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

// Patch WebClient to show AppsMenu instead of default app
patch(WebClient.prototype, {
    setup() {
        super.setup();
        // Read apps_menu optionally so isolated core WebClient tests (which do
        // not start this service) keep working once web_responsive is installed.
        this.appsMenuService = this.env.services.apps_menu;
    },
    _loadDefaultApp() {
        // The preference travels on session_info (see models/ir_http.py), so no
        // per-boot RPC is needed and the optional chain stays falsy - never
        // throwing - in isolated core tests that ship no session.apps_menu.
        //
        // 17.0's 221946b guarded the same "never throw in a stripped-down test
        // env" intent a different way, via registry.contains("apps_menu"). That
        // check is NOT forward-ported: at 18.0 this action registers under the
        // tag "menu" (see apps_menu_service.js), so the literal 17.0 condition
        // would be permanently false and would disable the redirect outright.
        // The session-marker guard above already covers the isolated-env case -
        // a mock session carries no apps_menu key - and webclient.test.js pins
        // both that case and the service-absent case.
        if (this.appsMenuService && session.apps_menu?.is_redirect_home) {
            return this.appsMenuService.toggleMenu(true);
        }
        return super._loadDefaultApp();
    },
});
