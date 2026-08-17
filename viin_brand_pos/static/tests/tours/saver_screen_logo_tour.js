/** @odoo-module **/
/* global posmodel */

// Positive-evidence oracle: proves the Viindoo logo actually RENDERS on the
// SaverScreen after the xpath fix in saver_screen.xml - not merely that the
// screen fails to crash. Core's own SaverScreenCloseOverlaysTour
// (point_of_sale/static/tests/pos/tours/saver_screen_tour.js) only asserts
// that overlays (dialogs/dropdowns) close when the SaverScreen shows; it
// would pass identically even if this module's override were deleted
// outright and the stock Odoo logo (or no logo at all) rendered instead.
//
// Steps 1-2 below (Chrome.startPoS(), then navigate("SaverScreen") from a
// "body" trigger) are lifted verbatim from that core tour - a known-good way
// to reach the SaverScreen from the POS login screen in a test session.
//
// Before the production fix: viin_brand_pos/static/src/app/screens/
// saver_screen.xml's dead xpath ("//div/img") raises an OwlError the first
// time OWL tries to render point_of_sale.SaverScreen, which destroys the
// whole POS root component (see the module's coding_guidelines-cited
// runbot trace). The SaverScreen never mounts, so the
// ".login-overlay .pos-logo" trigger below never appears and this tour
// FAILS BY TIMEOUT - RED for the actual production defect, not a narrower
// symptom of it.
//
// After the fix: the SaverScreen mounts and its ".pos-logo" div carries the
// "--navbar-logo" CSS custom property this module's override sets, which
// core's own navbar.scss consumes via
// `background-image: var(--navbar-logo, url(".../odoo_logo.svg"))` - the
// SAME mechanism, and the SAME shared ".pos-logo" class, this module
// already uses successfully on the navbar (navbar.xml). The assertion below
// reads the browser's OWN computed style, never re-deriving the expected
// value from the override's source - it just checks the resolved
// background-image names the Viindoo asset this module has always shipped
// for this screen (Viindoo-logo-slogan-half-inverted.svg).
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
