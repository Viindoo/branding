import { animationFrame, beforeEach, describe, expect, test } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";
import { Dialog } from "@web/core/dialog/dialog";
import { ClientErrorDialog, ErrorDialog, NetworkErrorDialog } from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";
import {
    allowTranslations,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { downloadReport } from "@web/webclient/actions/reports/utils";
import { setupPosEnv } from "@point_of_sale/../tests/unit/utils";
import { definePosModels } from "@point_of_sale/../tests/unit/data/generate_model_definitions";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { reportService } from "@point_of_sale/app/services/report_service";
import "@viin_brand_pos/app/errors/error_dialogs";
import { CORE_SCAN_AUTHORIZATION } from "@viin_brand_pos/app/screens/product_screen/product_screen";
import { CORE_WORKERS_MESSAGE } from "@viin_brand_pos/app/services/report_service";

// The unit bundle merges in web.assets_backend: viin_brand_web's dialog titles are de-branded here
// even without the POS bundle wiring, which tests/test_pos_brand_help.py and the customer-display
// HttpCase in tests/test_customer_display_render.py guard against the real bundles.

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
    expect(".o_error_detail pre").not.toHaveText("");
});

test("a refused camera permission does not name Odoo in the scan error", () => {
    const logged = [];
    patchWithCleanup(console, { error: (error) => logged.push(error) });
    const getter = Object.getOwnPropertyDescriptor(
        ProductScreen.prototype,
        "barcodeVideoScannerProps"
    ).get;
    const props = getter.call({ barcodeReader: { scan() {} } });

    props.onError(new Error(`Could not start scanning. ${_t(CORE_SCAN_AUTHORIZATION)}`));

    expect(logged).toHaveLength(1);
    expect(logged[0].message).not.toInclude("Odoo");
});

test("another scan error passes through untouched", () => {
    const logged = [];
    patchWithCleanup(console, { error: (error) => logged.push(error) });
    const props = Object.getOwnPropertyDescriptor(
        ProductScreen.prototype,
        "barcodeVideoScannerProps"
    ).get.call({ barcodeReader: { scan() {} } });
    const error = new Error("Could not start scanning. No device can be found.");

    props.onError(error);

    expect(logged).toEqual([error]);
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
