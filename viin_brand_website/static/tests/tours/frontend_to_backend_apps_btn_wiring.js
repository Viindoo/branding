import { registry } from "@web/core/registry";

/**
 * The frontend header's apps button must give a user pending-icon feedback on click. The button
 * is a sibling of #wrapwrap, so only the real rendered page proves the click wiring reaches it.
 */
registry.category("web_tour.tours").add("viin_brand_website_frontend_to_backend_apps_btn_wiring", {
    url: "/",
    steps: () => [
        {
            content:
                "The apps button renders outside #wrapwrap; arm a guard that blocks navigation",
            trigger:
                "body > .o_frontend_to_backend_nav > .o_frontend_to_backend_buttons > " +
                ".o_frontend_to_backend_apps_btn",
            run: () => {
                // Registered after the module's own document click listener, so it runs after
                // that handler and the next step reads the icon state a user sees before the
                // navigation starts.
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
            content: "The anchor itself never carries fa-spin, only the child spinner does",
            trigger: ".o_frontend_to_backend_apps_btn:not(.fa-spin)",
        },
    ],
});
