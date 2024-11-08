/** @odoo-module **/

import { session } from "@web/session";
import { onMounted } from "@odoo/owl";
import { AppsMenuAction } from "@web_responsive/components/apps_menu/apps_menu_service";
import { patch } from "@web/core/utils/patch";


patch(AppsMenuAction.prototype, {
    setup() {
        super.setup();
        onMounted(() => {
            this.theme = session.apps_menu.theme || "viindoo";
            document.body.setAttribute('data-theme', this.theme);
        })
    },
});


