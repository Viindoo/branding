import { t } from "@odoo/owl";
import { ActionDialog } from "@web/webclient/actions/action_dialog";

// ActionDialog spreads `dialogProps` into its own schema when its class is defined, so it holds
// its own copy of the title element.
ActionDialog.propsSchema.title = t.string().optional("Viindoo");
