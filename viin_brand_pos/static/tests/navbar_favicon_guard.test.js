/** @odoo-module **/

import { expect, getFixture, test } from "@odoo/hoot";

import { setupPosEnv } from "@point_of_sale/../tests/unit/utils";
import { definePosModels } from "@point_of_sale/../tests/unit/data/generate_model_definitions";
import { mountWithCleanup } from "@web/../tests/web_test_helpers";

import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
import "@viin_brand_pos/app/navbar/navbar";

definePosModels();

// The patched Navbar.setup() overwrites the href of every non-apple-touch-icon <link rel*="icon">
// with the favicon of the POS company. The real Navbar is mounted through OWL because usePos()
// needs a live component context; the expected company id is read from the same store.
test("branded POS navbar setup() sets the favicon from the current company when one is available", async () => {
    const icon = document.createElement("link");
    icon.rel = "icon";
    icon.href = "/original-favicon.ico";
    getFixture().appendChild(icon);

    const store = await setupPosEnv();
    await mountWithCleanup(Navbar, {});

    expect(icon.getAttribute("href")).toBe(`/web/image/res.company/${store.company.id}/favicon`);
});
