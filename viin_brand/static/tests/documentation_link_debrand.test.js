import { describe, expect, test } from "@odoo/hoot";

// Core DocumentationLink widget (web/static/src/views/widgets/documentation_link/documentation_link.js):
// `super.url` returns the "documentation" attribute unmodified when it is already an absolute
// URL, or `https://www.odoo.com/documentation/<server-version>` + the relative `path` prop
// otherwise. Importing the viin_brand patch as a side effect applies its mutation of
// `DocumentationLink.prototype.url` before any test body executes.
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import "@viin_brand/views/widgets/documentation_link/documentation_link";

describe.current.tags("headless");

/** Call the patched `url` getter with a fake widget instance, as Odoo's OWL template does at
 * render time (`t-att-href="url"` in web.DocumentationLink). */
function computedUrl(path) {
    return Reflect.get(DocumentationLink.prototype, "url", { props: { path } });
}

// Business rule under protection: a documentation link never reaches odoo.com. A mapped key opens
// the Viindoo page, a key mapped to "" or an unmapped odoo.com URL hides the link (the widget's own
// `t-if="url"` override, documentation_link.xml, hides it when the patched getter returns a falsy
// URL, so asserting the getter returns "" is asserting the link disappears), and a link to a third
// party keeps its URL.

const VIINDOO_DOCUMENTATION = "https://viindoo.com/documentation/19.0/";

test("Settings > Users documentation link opens the Viindoo user guide", () => {
    // base_setup ships this as a relative path ("/applications/general/users.html"), so
    // super.url version-substitutes it to the running server's series (19.0 here).
    expect(
        computedUrl("https://www.odoo.com/documentation/19.0/applications/general/users.html")
    ).toBe(
        VIINDOO_DOCUMENTATION +
            "applications/getting-started/manage-users/user-account-setting-and-management.html"
    );
});

test("Settings > Discuss custom ICE server documentation links open the Viindoo page", () => {
    // mail hardcodes these as an absolute URL with a literal "latest" segment (not a relative
    // path), so they never go through version substitution at all - the mapping must key on
    // the literal "latest" URL.
    const page =
        VIINDOO_DOCUMENTATION +
        "applications/productivity/discuss/set-up-calls-with-twilio-and-ice-servers.html";
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/latest/applications/productivity/discuss/ice_servers.html"
        )
    ).toBe(page);
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/latest/applications/productivity/discuss/ice_servers.html#define-a-list-of-custom-ice-servers"
        )
    ).toBe(page);
});

test("a link to a feature that Viindoo hides is mapped to an empty URL", () => {
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/19.0/applications/general/in_app_purchase.html"
        )
    ).toBe("");
});

test("the Vietnam localization link opens the Viindoo S-Invoice guide", () => {
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/vietnam.html"
        )
    ).toBe(
        VIINDOO_DOCUMENTATION +
            "applications/finance/accounting-and-invoicing/fiscal-localizations/issue-e-invoice-by-integrating-viindoo-with-viettel-s-s-invoice-service.html"
    );
});

test("corrected links open the page of their own setting", () => {
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/default_taxes.html"
        )
    ).toBe(
        VIINDOO_DOCUMENTATION +
            "applications/finance/accounting-and-invoicing/taxation/default-taxes.html"
    );
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/19.0/applications/productivity/mail_plugins.html"
        )
    ).toBe("");
});

test("an unmapped odoo.com documentation link is hidden", () => {
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/19.0/applications/a/page/nobody/mapped.html"
        )
    ).toBe("");
    expect(computedUrl("https://www.odoo.com/documentation/master/developer/unmapped.html")).toBe(
        ""
    );
    expect(computedUrl("https://odoo.com/app/unmapped")).toBe("");
});

test("a link to a third party keeps its URL", () => {
    expect(computedUrl("https://developers.google.com/maps/documentation")).toBe(
        "https://developers.google.com/maps/documentation"
    );
    expect(computedUrl("https://example.com/odoo.com/page")).toBe(
        "https://example.com/odoo.com/page"
    );
});
