import { patchWithCleanup } from "@web/../tests/web_test_helpers";
import { setupPosEnv } from "@point_of_sale/../tests/unit/utils";
import { WebSerialScaleInterface } from "@point_of_sale/app/utils/scale/web_serial_scale_interface";

/**
 * `setupPosEnv` for a test that is not about a scale.
 *
 * The POS store connects the electronic scales while it starts. The Web Serial one asks the browser
 * for its granted ports, an answer that a browser can hold back for many seconds, so a POS test
 * that runs early in a page waits for the real browser instead of for the code under test.
 */
export async function setupPosEnvWithoutScale(...args) {
    patchWithCleanup(WebSerialScaleInterface.prototype, { connectToScale: async () => false });
    return setupPosEnv(...args);
}
