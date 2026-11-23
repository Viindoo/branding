import { describe, expect, test } from "@odoo/hoot";
import { allowTranslations, mountWithCleanup } from "@web/../tests/web_test_helpers";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import "@viin_brand_mysubscription/user_menu";

describe.current.tags("desktop");

test("the user menu offers no entry that opens the dashboard of the Odoo plans", async () => {
    allowTranslations();
    const userMenu = await mountWithCleanup(UserMenu);

    const items = userMenu.getElements();

    // an empty menu would satisfy the check below trivially
    expect(items.length).toBeGreaterThan(0);
    expect(items.map((item) => item.id)).not.toInclude("mysubscription_user_menu");
});
