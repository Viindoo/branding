import { components } from "@odoo/o-spreadsheet";
import { patch } from "@web/core/utils/patch";

const CHART_LINK_ITEM_ID = "chartOdooLink";

// The entry that opens the record a chart is linked to is labelled with the product name.
patch(components.ChartMenu.prototype, {
    getMenuItems() {
        const items = super.getMenuItems();
        for (const item of items) {
            if (item.id === CHART_LINK_ITEM_ID) {
                item.label = String(item.label).replaceAll("Odoo", "Viindoo");
            }
        }
        return items;
    },
});
