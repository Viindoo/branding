/** @odoo-module **/

import { UpgradeDialog } from "@web/webclient/settings_form_view/fields/upgrade_dialog";
import { patch } from "@web/core/utils/patch";

// De-brand the Enterprise-upsell dialog's primary CTA (PR #633 rebase verdict c2-common.md
// finding R-7): the dialog's TEMPLATE was de-branded (see upgrade_dialog.xml, same directory),
// but core's `_confirmUpgrade()` was never patched, so clicking "Upgrade now" still sent the
// customer to odoo.com - a half-finished de-brand shipping a Viindoo-styled dialog with an Odoo
// destination underneath it.
//
// Core (web/static/src/webclient/settings_form_view/fields/upgrade_dialog.js, 19.0):
//     async _confirmUpgrade() {
//         const usersCount = await this.orm.call("res.users", "search_count", [...]);
//         window.open("https://www.odoo.com/odoo-enterprise/upgrade?num_users=" + usersCount, ...);
//         this.props.close();
//     }
//
// We replace the method WITHOUT calling `super()`: core's entire body exists only to compute
// `num_users` for the odoo.com URL and then open it - both steps are undesired here (there is no
// Viindoo equivalent of the num_users-qualified odoo.com upgrade endpoint), so extending it would
// mean calling super() then discarding/overriding its side effect, which is more convoluted than
// a clean full replacement. We open the SAME viindoo.com/pricing URL already used by this dialog's
// own "And more" link (see upgrade_dialog.xml) - the one already-established Viindoo
// enterprise-upsell destination in this exact context - then call `this.props.close()` exactly as
// core does, so the dialog still closes on click.
patch(UpgradeDialog.prototype, {
    _confirmUpgrade() {
        window.open("https://viindoo.com/pricing?utm_source=db&utm_medium=enterprise", "_blank");
        this.props.close();
    },
});
