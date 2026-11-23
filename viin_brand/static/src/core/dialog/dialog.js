import { t } from "@odoo/owl";
import { dialogProps } from "@web/core/dialog/dialog";

// A dialog opened without an explicit `title` shows the Viindoo wordmark, never the stock one.
// `Dialog.propsSchema` is `dialogProps`, so the element is replaced in place.
dialogProps.title = t.string().optional("Viindoo");
