import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { _t } from "@web/core/l10n/translation";
import { allowTranslations, onRpc } from "@web/../tests/web_test_helpers";
import { downloadReport } from "@web/webclient/actions/reports/utils";
import { setupPosEnvWithoutScale } from "@viin_brand_pos/../tests/pos_test_env";
import { definePosModels } from "@point_of_sale/../tests/unit/data/generate_model_definitions";
import { reportService } from "@point_of_sale/app/services/report_service";
import { CORE_WORKERS_MESSAGE } from "@viin_brand_pos/app/services/report_service";

// The unit bundle merges in web.assets_backend, so the dialog files of viin_brand load here; the POS
// bundle wiring is guarded by tests/test_pos_brand_help.py and tests/test_customer_display_render.py.

definePosModels();

describe.current.tags("headless");

beforeEach(() => {
    allowTranslations();
});

test("the report download failure for missing workers does not name Odoo", async () => {
    await setupPosEnvWithoutScale();
    onRpc("/web/action/load", () => ({ type: "ir.actions.report", report_type: "qweb-pdf" }));
    onRpc("/report/get_pdf_engine_state", () => "workers");
    downloadReport.reportingEngineStatusProm = null;
    const service = reportService.start({}, { ui: { block() {}, unblock() {} }, orm: {}, pos: {} });

    const result = await service.doAction("point_of_sale.report", [1]);

    expect(result.success).toBe(false);
    expect(result.message).not.toInclude("Odoo");
    expect(result.message).not.toBe(_t(CORE_WORKERS_MESSAGE).toString());
    downloadReport.reportingEngineStatusProm = null;
});
