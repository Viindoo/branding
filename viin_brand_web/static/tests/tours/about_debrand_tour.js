import { registry } from "@web/core/registry";

// Business rule under protection: the "About" block of General Settings (rendered by the core
// `res_config_edition` view-widget) must display the Viindoo brand, and must NOT display the stock
// Odoo brand strings, after viin_brand_web is installed. viin_brand_web overrides the core
// `res_config_edition` QWeb template (static/src/core/webclient/settings_form_view/widgets/
// res_config_edition.xml, t-inherit) so that:
//   - the version <h3> reads "Viindoo <serverVersion>" instead of "Odoo <serverVersion> (Community Edition)"
//   - the copyright <small> reads "... Viindoo. ... GNU LGPL Licensed" instead of "... Odoo S.A. ..."
// The widget is placed inside <div id="about"> on the General Settings form
// (base_setup/views/res_config_settings_views.xml). If the override is missing or broken, the
// stock "Odoo <version>" heading / "Odoo S.A." copyright reappear and the negative-assertion
// triggers below never match -> the tour times out -> the HttpCase fails (red for the right reason).
//
// Tour selectors are case-insensitive :contains (grounded against v19 core tours); the negative
// assertions use the grounded `:not(:has(el:contains(...)))` idiom.
registry.category("web_tour.tours").add("viin_brand_web_about_debrand", {
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
            content: "About heading no longer shows the stock Odoo brand",
            trigger: "#about:not(:has(h3:contains('Odoo')))",
        },
        {
            content: "About copyright no longer shows the stock 'Odoo S.A.' credit",
            trigger: "#about:not(:has(a:contains('Odoo S.A.')))",
        },
    ],
});
