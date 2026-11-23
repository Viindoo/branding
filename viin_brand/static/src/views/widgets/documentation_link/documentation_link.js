import { patch } from "@web/core/utils/patch";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import { ODOO_VIINDOO_DOCUMENTATION_MAPPING } from "./viindoo_mapping_url";

const ODOO_HOST = /(^|\.)odoo\.com$/;
// A page of the Odoo documentation: the series segment (`19.0`, `saas~19.1`, `latest`, `master`)
// is dropped, so that a final build and a development build look up the same entry.
const ODOO_DOCUMENTATION_PAGE =
    /^https?:\/\/(?:www\.)?odoo\.com\/documentation\/(?:\d+\.\d+|saas~\d+\.\d+|latest|master)(\/.*)$/;

patch(DocumentationLink.prototype, {
    get url() {
        const originalUrl = super.url;
        const path = originalUrl.match(ODOO_DOCUMENTATION_PAGE)?.[1];
        // A mapped value replaces the URL. An empty string hides the link (the template renders
        // it only when `url` is truthy). An unmapped link to odoo.com is hidden too, never shown;
        // a link to a third party keeps its URL.
        if (path && Object.hasOwn(ODOO_VIINDOO_DOCUMENTATION_MAPPING, path)) {
            return ODOO_VIINDOO_DOCUMENTATION_MAPPING[path];
        }
        if (ODOO_HOST.test(new URL(originalUrl, window.location.href).hostname)) {
            return "";
        }
        return originalUrl;
    },
});
