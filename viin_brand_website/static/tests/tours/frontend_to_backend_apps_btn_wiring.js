import { registry } from "@web/core/registry";

/**
 * Business rule under protection: the frontend header's apps button
 * (static/src/js/frontend_to_backend_apps_btn.js) must give a real user pending-icon feedback on
 * click. A unit test alone cannot prove the wiring is actually live: website.layout renders the
 * button as a SIBLING of #wrapwrap, never a descendant of it, so this drives the real rendered
 * page - no fabricated ancestor - and fails loudly if a future Odoo ever nests the button back
 * inside #wrapwrap.
 */
registry.category("web_tour.tours").add("viin_brand_website_frontend_to_backend_apps_btn_wiring", {
    url: "/",
    steps: () => [
        {
            content:
                "The apps button renders outside #wrapwrap; arm a click guard that blocks navigation",
            trigger:
                "body > .o_frontend_to_backend_nav > .o_frontend_to_backend_buttons > " +
                ".o_frontend_to_backend_apps_btn",
            run: () => {
                // Registered here, at tour-step time, strictly AFTER the production module's own
                // listener already registered at page load - both bind "click" on `document` in
                // the default (bubble) phase, so listener REGISTRATION ORDER decides execution
                // order: this guard always runs after the button's own handler already ran, so
                // the icon state the next step reads is exactly what a user would see before
                // navigation actually starts.
                document.addEventListener("click", (ev) => ev.preventDefault());
            },
        },
        {
            content: "Click the apps button",
            trigger: ".o_frontend_to_backend_apps_btn",
            run: "click",
        },
        {
            content:
                "The icon swapped to a dedicated pending-spinner child; the anchor's own " +
                "static glyph class is gone",
            trigger:
                ".o_frontend_to_backend_apps_btn:not(.fa-th) > " +
                ".o_viin_apps_btn_spinner.fa-circle-o-notch.fa-spin",
        },
        {
            content:
                "The anchor itself never carries fa-spin - only the child spinner does, so a " +
                "regression that spins the whole button again fails here instead of passing",
            trigger: ".o_frontend_to_backend_apps_btn:not(.fa-spin)",
        },
    ],
});
