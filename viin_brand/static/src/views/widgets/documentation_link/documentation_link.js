/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import { ODOO_VIINDOO_DOCUMENTATION_MAPPING } from "./viindoo_mapping_url";

patch(DocumentationLink.prototype, {
    get url() {
        const original_url = super.url;
        // The map is keyed on final-build 19.0 URLs; a non-final build yields a "master" segment
        // that would miss every key, so it is normalized back to the 19.0 key.
        const lookupKey = original_url.replace(
            "https://www.odoo.com/documentation/master/",
            "https://www.odoo.com/documentation/19.0/"
        );
        // A mapped value replaces the URL. An empty string hides the link (the template renders
        // it only when `url` is truthy) and an absent key keeps the original URL.
        const mapped = ODOO_VIINDOO_DOCUMENTATION_MAPPING[lookupKey];
        if (mapped !== undefined) {
            return mapped;
        }
        return original_url;
    },
});
