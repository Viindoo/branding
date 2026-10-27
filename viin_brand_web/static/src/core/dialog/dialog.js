/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// ActionDialog copies Dialog.defaultProps when core defines it, so it keeps "Odoo" unless it is
// branded itself. Importing it also guarantees it is defined before this file brands it.
for (const component of [Dialog, ActionDialog]) {
    component.defaultProps.title = component.defaultProps.title.replace(/Odoo/g, "Viindoo");
}
