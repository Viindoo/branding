import { expect, test } from "@odoo/hoot";
import { mockPermission } from "@odoo/hoot-mock";
import { defineModels, models, mountView } from "@web/../tests/web_test_helpers";

// The blocked-notification alert says what happened, without a product name in front of it.

class Partner extends models.Model {
    _records = [{ id: 1 }];
}

defineModels([Partner]);

test("the blocked push notification alert carries no product name", async () => {
    mockPermission("notifications", "denied");
    await mountView({
        type: "form",
        resModel: "partner",
        resId: 1,
        arch: /* xml */ `<form><widget name="notification_alert"/></form>`,
    });
    expect(".o_widget_notification_alert .alert").toHaveText(
        "Push notifications have been blocked. Go to your browser settings to allow them."
    );
});
