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
            content: "The icon of the button turned into the spinning pending icon",
            trigger:
                ".o_frontend_to_backend_apps_btn > i.oi.oi-spin[data-icon='progress_activity']",
        },
        {
            content: "The anchor itself never spins, only its icon does",
            trigger: ".o_frontend_to_backend_apps_btn:not(.oi-spin)",
        },
    ],
});
