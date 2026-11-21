import { OdooChartCorePlugin } from "@spreadsheet/chart/plugins/odoo_chart_core_plugin";
import { patch } from "@web/core/utils/patch";

// An untitled chart is listed under the name of its type ("Odoo Bar Chart"); a title the user
// typed is theirs and is left alone.
patch(OdooChartCorePlugin.prototype, {
    getOdooChartDisplayName(chartId) {
        const name = super.getOdooChartDisplayName(chartId);
        const { title } = this.getters.getChart(chartId);
        return title.text ? name : name.replaceAll("Odoo", "Viindoo");
    },
});
