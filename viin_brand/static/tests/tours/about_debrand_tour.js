import { registry } from "@web/core/registry";

// The "About" block of General Settings (rendered by the core `res_config_edition` view-widget)
// must display the Viindoo brand and not the stock Odoo brand strings. viin_brand overrides the
// core `res_config_edition` QWeb template (static/src/webclient/settings_form_view/widgets/
// res_config_edition.xml, t-inherit) so that:
//   - the version <h3> reads "Viindoo <serverVersion>" instead of "Odoo <serverVersion> (Community Edition)"
//   - the copyright <small> reads "... Viindoo. ... GNU LGPL Licensed" instead of "... Odoo S.A. ..."
// The widget is placed inside <div id="about"> on the General Settings form
// (base_setup/views/res_config_settings_views.xml). If the override is missing or broken, the
// stock "Odoo <version>" heading / "Odoo S.A." copyright remain and the negative-assertion
// triggers below never match, so the tour times out and the HttpCase fails.
//
// Tour selectors are case-insensitive :contains; the negative assertions use the
// `:not(:has(el:contains(...)))` idiom.
registry.category("web_tour.tours").add("viin_brand_about_debrand", {
    url: "/odoo/settings",
    steps: () => [
        {
            content: "About heading shows the Viindoo brand (de-branded from Odoo)",
            trigger: "#about h3:contains('Viindoo')",
        },
        {
            content: "About copyright shows the Viindoo brand (de-branded from Odoo S.A.)",
            trigger: "#about small:contains('Viindoo')",
        },
        {
            content: "About heading does not show the stock Odoo brand",
            trigger: "#about:not(:has(h3:contains('Odoo')))",
        },
        {
            content: "About copyright does not show the stock 'Odoo S.A.' credit",
            trigger: "#about:not(:has(a:contains('Odoo S.A.')))",
        },
    ],
});
