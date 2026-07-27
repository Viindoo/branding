/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import { ODOO_VIINDOO_DOCUMENTATION_MAPPING } from "./viindoo_mapping_url";

patch(DocumentationLink.prototype, {
    get url() {
        const original_url = super.url;
        // Core's web.DocumentationLink builds ".../documentation/<version>/..." where <version> is
        // "X.Y" on a FINAL build and "master" on a NON-FINAL build (mirrors session.server_version_info;
        // documentation_link.js get url). This map is keyed on the FINAL 19.0 URLs, so on a non-final
        // 19.0 build core computes a "master" URL that would miss every key and leak the odoo.com
        // link. Normalize the master segment back to the 19.0 key namespace so the Viindoo override
        // fires on non-final builds too (bumping the whole map to a new series is a separate pass).
        const lookupKey = original_url.replace(
            "https://www.odoo.com/documentation/master/",
            "https://www.odoo.com/documentation/19.0/"
        );
        // An empty-string value is a DELIBERATE suppression (no Viindoo page yet): the template
        // patch (documentation_link.xml, t-if="url") then HIDES the link rather than leaking
        // www.odoo.com - so return the mapped value verbatim, empty string included.
        const mapped = ODOO_VIINDOO_DOCUMENTATION_MAPPING[lookupKey];
        if (mapped !== undefined) {
            return mapped;
        }
        return original_url;
    },
});
