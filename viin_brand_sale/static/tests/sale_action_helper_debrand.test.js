import { expect, test } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";
import { mockService, mountWithCleanup } from "@web/../tests/web_test_helpers";
import { defineSaleModels } from "@sale/../tests/sale_test_helpers";

import { SaleActionHelper } from "@sale/js/sale_action_helper/sale_action_helper";
import "@viin_brand_sale/js/sale_action_helper/sale_action_helper";

defineSaleModels();

test("the quotation onboarding video is the one of Viindoo, not the video of Odoo", async () => {
    const opened = [];
    mockService("dialog", {
        add(component, props) {
            opened.push(props);
        },
    });
    await mountWithCleanup(SaleActionHelper, { props: { noContentHelp: "" } });

    await click(".o_sale_action_preview");

    expect(opened).toHaveLength(1);
    const url = new URL(opened[0].url);
    expect(url.origin + url.pathname.replace(/[^/]+$/, "")).toBe("https://www.youtube.com/embed/");
    // the id of the video Odoo ships on the same screen
    expect(url.pathname).not.toInclude("N4zw-2t6spk");
});
