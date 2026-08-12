import { describe, expect, test } from "@odoo/hoot";

// Core DocumentationLink widget (web/static/src/views/widgets/documentation_link/documentation_link.js):
// `super.url` returns the "documentation" attribute unmodified when it is already an absolute
// URL, or `https://www.odoo.com/documentation/<server-version>` + the relative `path` prop
// otherwise. Import the REAL, unmodified viin_brand_web patch as a side effect so the
// mutation it applies to `DocumentationLink.prototype.url` runs before any test body executes
// (same idiom as viin_brand_web's dialog_debrand.test.js).
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import "@viin_brand_web/views/widgets/documentation_link/documentation_link";

describe.current.tags("headless");

/** Call the REAL (patched) `url` getter with a fake widget instance, mirroring exactly what
 * Odoo's OWL template invokes at render time (`t-att-href="url"` in web.DocumentationLink). */
function computedUrl(path) {
    return Reflect.get(DocumentationLink.prototype, "url", { props: { path } });
}

// Business rule under protection (live-acceptance OBS-1): a core settings field whose computed
// Odoo documentation URL has no Viindoo replacement mapped must never leak a live www.odoo.com
// link onto Settings > General Settings - the widget's own `t-if="url"` override
// (documentation_link.xml) hides the link entirely when the patched getter returns a falsy ("")
// URL, so asserting the getter itself returns "" is asserting the link disappears.

test("Settings > Users documentation link never leaks to www.odoo.com", () => {
    // base_setup ships this as a relative path ("/applications/general/users.html"), so
    // super.url version-substitutes it to the running server's series (19.0 here).
    expect(
        computedUrl("https://www.odoo.com/documentation/19.0/applications/general/users.html")
    ).toBe("");
});

test("Settings > Discuss custom ICE server documentation links never leak to www.odoo.com", () => {
    // mail hardcodes these as an absolute URL with a literal "latest" segment (not a relative
    // path), so they never go through version substitution at all - the mapping must key on
    // the literal "latest" URL.
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/latest/applications/productivity/discuss/ice_servers.html"
        )
    ).toBe("");
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/latest/applications/productivity/discuss/ice_servers.html#define-a-list-of-custom-ice-servers"
        )
    ).toBe("");
});

test("Settings > Geolocation documentation link never leaks to www.odoo.com", () => {
    // base_setup ships this as a relative path too, version-substituted the same way as Users.
    expect(
        computedUrl(
            "https://www.odoo.com/documentation/19.0/applications/general/integrations/geolocation.html"
        )
    ).toBe("");
});
