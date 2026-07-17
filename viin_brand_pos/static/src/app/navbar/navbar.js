/** @odoo-module **/

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    /**
     * @override
     */
    setup() {
        super.setup();
        // copy from to_base
        // The company service is not registered in the bare POS QUnit test env
        // (point_of_sale.tests.test_js "mount the Chrome"), so guard it: without a
        // current company there is no branded favicon to set, just skip.
        const currentCompany = this.env.services.company?.currentCompany;
        if (!currentCompany) {
            return;
        }
        const favicon = `/web/image/res.company/${currentCompany.id}/favicon`;
        const icons = document.querySelectorAll("link[rel*='icon']");
        for (const icon of icons) {
            if (icon.rel != "apple-touch-icon") {
                icon.href = favicon;
            }
        }
    },
});
