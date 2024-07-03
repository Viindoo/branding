/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import { ODOO_VIINDOO_DOCUMENTATION_MAPPING } from './viindoo_mapping_url';


patch(DocumentationLink.prototype, {
    get url() {
        let original_url = super.url;
        if (ODOO_VIINDOO_DOCUMENTATION_MAPPING[original_url] !== undefined){
            return ODOO_VIINDOO_DOCUMENTATION_MAPPING[original_url];
        }
        return original_url;
    }
});
