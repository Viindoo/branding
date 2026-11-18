/** @odoo-module **/

// Route the Discuss onboarding tour through the theme's flat home-menu landing. The theme lands
// `/odoo` on the home menu (webclient_patch.js), while core's `discuss_channel_tour` has a CE step
// that assumes Discuss is already open (`.o-mail-DiscussSearch-inputContainer`). One navigation step
// is prepended that opens Discuss from its home-menu tile (`.o_app[data-menu-xmlid=...]`, home_menu.xml)
// before that step; no assertion is weakened.
//
// The step is CE-scoped (`isActive: ["community"]`, the counterpart of core step 0's
// `["enterprise"]` gate) and its trigger only exists under the theme's home-menu landing. The tour is
// registered by mail, which the theme depends on; the `contains` guard is defensive.

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

const tourRegistry = registry.category("web_tour.tours");

if (tourRegistry.contains("discuss_channel_tour")) {
    patch(tourRegistry.get("discuss_channel_tour"), {
        steps() {
            return [
                {
                    isActive: ["community"],
                    trigger: ".o_viin_home_menu .o_app[data-menu-xmlid='mail.menu_root_discuss']",
                    content: _t("Open the Discuss app from the Applications home menu."),
                    tooltipPosition: "bottom",
                    run: "click",
                },
                ...super.steps(),
            ];
        },
    });
}
