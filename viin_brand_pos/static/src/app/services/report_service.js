import { reportService } from "@point_of_sale/app/services/report_service";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// Plain constant, not a literal _t(): looked up in core's catalog, not copied into ours.
export const CORE_WORKERS_MESSAGE =
    "You need to start Odoo with at least two workers to print a pdf version of the reports.";

/** Swap core's missing-workers message in a failed report download result. */
export function withNeutralReportMessage(result) {
    if (result && result.message && result.message === _t(CORE_WORKERS_MESSAGE).toString()) {
        return {
            ...result,
            message: _t(
                "You need to start the server with at least two workers to print a pdf version of the reports."
            ),
        };
    }
    return result;
}

patch(reportService, {
    start(env, deps) {
        const service = super.start(env, deps);
        const doAction = service.doAction;
        return {
            ...service,
            async doAction() {
                return withNeutralReportMessage(await doAction(...arguments));
            },
        };
    },
});
