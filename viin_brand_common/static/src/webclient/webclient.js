/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        // Server-stamped session marker (see viin_brand_common ir_http): only
        // brand real sessions. Core ActionManager QUnit suites assert the
        // default "Odoo" title part and the marker is absent from their mock
        // sessions (runbot 223235/396399, 3 title/pushState tests).
        if (session.viin_brand) {
            this.title.setParts({ zopenerp: "Viindoo" });
        }
    },
});
