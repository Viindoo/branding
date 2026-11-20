import { expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-dom";
import { mountWithCleanup, patchWithCleanup } from "@web/../tests/web_test_helpers";

import { browser } from "@web/core/browser/browser";
import { BarcodeVideoScanner } from "@web/core/barcode/barcode_video_scanner";
import "@viin_brand/core/barcode/barcode_video_scanner";

// A refused camera permission is reported to the consumer of the scanner (the barcode dialog, the
// point of sale screens) with the Viindoo name, whoever the consumer is.

async function scanWithCameraError(error) {
    patchWithCleanup(browser.navigator, {
        mediaDevices: { getUserMedia: () => Promise.reject(error) },
    });
    const errors = [];
    await mountWithCleanup(BarcodeVideoScanner, {
        props: {
            facingMode: "environment",
            onReady: () => {},
            onResult: () => {},
            onError: (scanError) => errors.push(scanError.message),
        },
    });
    await animationFrame();
    await animationFrame();
    return errors;
}

test("a refused camera permission names Viindoo", async () => {
    const errors = await scanWithCameraError({ name: "NotAllowedError" });
    expect(errors).toHaveLength(1);
    expect(errors[0]).toMatch(/Viindoo/);
    expect(errors[0]).not.toMatch(/Odoo/);
});

test("an error that is not a refused permission is passed on unchanged", async () => {
    const errors = await scanWithCameraError({ name: "NotFoundError" });
    expect(errors).toEqual(["Could not start scanning. No device can be found."]);
});
