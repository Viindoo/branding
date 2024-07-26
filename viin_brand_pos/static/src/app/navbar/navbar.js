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
        const favicon = `/web/image/res.company/${this.env.services.company.currentCompany.id}/favicon`;
        const icons = document.querySelectorAll("link[rel*='icon']");
        for (const icon of icons) {
            if (icon.rel != 'apple-touch-icon') {
                icon.href = favicon;
            }
        }
    }
});
