/** @odoo-module **/

// R2 (PR #658) - route the Discuss onboarding through the theme's flat home-menu landing.
//
// PROBLEM (proven: mail TestUi.test_01_mail_tour + test_02_mail_create_channel_no_mail_tour fail on
// the themed build, stock passes). The theme's WebClient._loadDefaultApp (webclient_patch.js) lands
// `/odoo` on the flat "Applications" home menu (D3) instead of core CE's first root app (Discuss).
// Core's `discuss_channel_tour` has an enterprise-only first step and then a CE-active step that
// assumes Discuss is ALREADY open (`.o-mail-DiscussSearch-inputContainer`), so under the themed
// landing that search container never appears and the tour fails at its first CE step. The D3
// landing is an INTENDED feature - it must NOT be reverted.
//
// FIX. Prepend ONE navigation step that, on the themed CE landing, opens Discuss by clicking its
// home-menu tile BEFORE the search-container step. No real assertion is weakened or skipped - only
// the navigation the themed landing removed is added back. Grounded (OSM 19.0 + core source):
//   - the tour is `registry.category("web_tour.tours").get("discuss_channel_tour")`
//     (mail/static/src/js/tours/discuss_channel_tour.js, shipped in mail's web.assets_backend); the
//     canonical v19 cross-module extend is `patch(tourObject, { steps() { return [...] } })` with
//     `super.steps()` (see crm_iap_mine / to_account_accountant).
//   - the Discuss root-menu xmlid is `mail.menu_root_discuss` (core tour step 0 selector); the
//     home-menu tiles expose `.o_app[data-menu-xmlid="<root menu xmlid>"]` (home_menu.xml).
//
// NO-OP ON A THEME-FREE INSTALL. This file loads only when viin_backend_theme is installed, so the
// core tour is untouched otherwise. The step is CE-scoped (`isActive: ["community"]`, mirroring core
// step 0's `["enterprise"]` gate - the two editions' Discuss-open arms), and its trigger only exists
// under the theme's home-menu landing. viin_backend_theme depends on mail (via viin_brand_mail), so
// the tour is always registered before this patch runs; the `contains` guard is defensive.

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
