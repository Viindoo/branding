import { animationFrame, beforeEach, describe, expect, test } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";
import { Dialog } from "@web/core/dialog/dialog";
import { ClientErrorDialog, ErrorDialog, NetworkErrorDialog } from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";
import { allowTranslations, mountWithCleanup, onRpc } from "@web/../tests/web_test_helpers";
import { downloadReport } from "@web/webclient/actions/reports/utils";
import { setupPosEnv } from "@point_of_sale/../tests/unit/utils";
import { definePosModels } from "@point_of_sale/../tests/unit/data/generate_model_definitions";
import { reportService } from "@point_of_sale/app/services/report_service";
import "@viin_brand/core/dialog/dialog";
import "@viin_brand/core/errors/error_dialogs";
import { CORE_WORKERS_MESSAGE } from "@viin_brand_pos/app/services/report_service";

// The unit bundle merges in web.assets_backend, so the dialog files of viin_brand load here; the POS
// bundle wiring is guarded by tests/test_pos_brand_help.py and tests/test_customer_display_render.py.

definePosModels();

describe.current.tags("headless");

beforeEach(() => {
    allowTranslations();
});

test("error dialog headings do not name Odoo", () => {
    for (const Dialog_ of [ErrorDialog, ClientErrorDialog, NetworkErrorDialog]) {
        expect(String(Dialog_.title)).not.toInclude("Odoo");
    }
});

test("a dialog opened without a title is not headed with the product name", () => {
    expect(String(Dialog.defaultProps.title)).not.toInclude("Odoo");
});

test("the technical details of an error dialog do not name Odoo", async () => {
    await setupPosEnv();
    await mountWithCleanup(ErrorDialog, {
        props: {
            close() {},
            traceback:
                "An error whose details cannot be accessed by the Odoo framework has occurred.\n" +
                "An unknown error occured. This may be due to a Chrome extension meddling with Odoo.",
        },
    });
    await animationFrame();
    expect(".o_error_dialog button.btn-link").toHaveCount(1);
    await click(".o_error_dialog button.btn-link");
    await animationFrame();
    expect(".o_error_detail pre").toHaveCount(1);
    expect(".o_error_detail pre").not.toHaveText(/Odoo/);
    expect(".o_error_detail pre").toHaveText(/by the Viindoo framework/);
    expect(".o_error_detail pre").toHaveText(/meddling with Viindoo/);
});

test("the report download failure for missing workers does not name Odoo", async () => {
    await setupPosEnv();
    onRpc("/web/action/load", () => ({ type: "ir.actions.report", report_type: "qweb-pdf" }));
    onRpc("/report/check_wkhtmltopdf", () => "workers");
    downloadReport.wkhtmltopdfStatusProm = null;
    const service = reportService.start({}, { ui: { block() {}, unblock() {} }, orm: {}, pos: {} });

    const result = await service.doAction("point_of_sale.report", [1]);

    expect(result.success).toBe(false);
    expect(result.message).not.toInclude("Odoo");
    expect(result.message).not.toBe(_t(CORE_WORKERS_MESSAGE).toString());
    downloadReport.wkhtmltopdfStatusProm = null;
});
