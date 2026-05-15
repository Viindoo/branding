/** @odoo-module **/

import {useService} from "@web/core/utils/hooks";
import {WebClient} from "@web/webclient/webclient";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";


// Patch WebClient to show AppsMenu instead of default app
patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.appsMenuService = useService("apps_menu");
        onWillStart(async () => {
            const is_redirect_home = await this.orm.searchRead(
                "res.users",
                [["id", "=", user.userId]],
                ["is_redirect_home"],
            );
            user.updateContext({
                is_redirect_to_home: is_redirect_home[0]?.is_redirect_home,
            });
        });
    },
    _loadDefaultApp() {
        return this.appsMenuService.toggleMenu(true);
        if (user.context.is_redirect_to_home) {
            return this.appsMenuService.toggleMenu(true);
        }
        return super._loadDefaultApp();
    }
});
