/** @odoo-module */
/* Copyright 2023 Onestein - Anjeel Haria
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import {patch} from "@web/core/utils/patch";
import {FormController} from "@web/views/form/form_controller";

// Patch FormController to always load attachment alongwith the chatter on the side bar
patch(FormController.prototype, "web_responsive.FormController", {
    setup() {
        // TODO: remove me in v17/master because viindoo Saas has been suffered errors from some removed JS files in stable version
        this._super();
    },
});
