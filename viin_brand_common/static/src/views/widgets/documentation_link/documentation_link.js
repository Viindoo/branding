/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import { ODOO_VIINDOO_DOCUMENTATION_MAPPING } from "./viindoo_mapping_url";

patch(DocumentationLink.prototype, {
    get url() {
        const original_url = super.url;
        const viindoo_url = ODOO_VIINDOO_DOCUMENTATION_MAPPING[original_url];
        if (viindoo_url) {
            return viindoo_url;
        }
        // Fallback: keep original Odoo link (working link > dead link)
        return original_url;
    },
});
