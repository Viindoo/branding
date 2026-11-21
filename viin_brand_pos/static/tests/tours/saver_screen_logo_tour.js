/** @odoo-module **/
/* global posmodel */

// Proves the Viindoo logo renders on the SaverScreen: its ".pos-logo" div carries the "--navbar-logo"
// custom property of this module, which core's navbar.scss consumes. The assertion reads the
// browser's own computed style.
import * as Chrome from "@point_of_sale/../tests/pos/tours/utils/chrome_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("ViinBrandPosSaverScreenLogoTour", {
    steps: () =>
        [
            Chrome.startPoS(),
            {
                trigger: "body",
                run: () => posmodel.navigate("SaverScreen"),
            },
            {
                content:
                    "Check the SaverScreen's .pos-logo resolves its background-image to " +
                    "the Viindoo asset (not the stock Odoo logo, and not a blank/crashed screen)",
                trigger: ".login-overlay .pos-logo",
                run: () => {
                    const logoEl = document.querySelector(".login-overlay .pos-logo");
                    const backgroundImage = getComputedStyle(logoEl).backgroundImage;
                    if (!backgroundImage.includes("Viindoo-logo-slogan-half-inverted.svg")) {
                        throw new Error(
                            "Expected the SaverScreen .pos-logo background-image to resolve " +
                                "to the Viindoo asset (Viindoo-logo-slogan-half-inverted.svg), " +
                                "got: " +
                                backgroundImage
                        );
                    }
                },
            },
            Chrome.endTour(),
        ].flat(),
});
