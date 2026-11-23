import { expect, test } from "@odoo/hoot";
import { animationFrame, queryText } from "@odoo/hoot-dom";
import { getService, makeTestApp, mountWithCleanup } from "@web/../tests/web_test_helpers";

import { _t } from "@web/core/l10n/translation";
import { NotificationPlugin } from "@web/core/notifications/notification_plugin";
import { registry } from "@web/core/registry";
import "@viin_brand/webclient/actions/reports/report_notification";

// The notification raised when a PDF report cannot be printed because the server runs without
// workers names Viindoo; every other notification is shown as it is.

async function mountNotifications() {
    await makeTestApp();
    const { Component, props } = registry.category("main_components").get("NotificationContainer");
    await mountWithCleanup(Component, { props, noMainContainer: true });
}

test("the missing workers notification names Viindoo", async () => {
    await mountNotifications();
    getService(NotificationPlugin).add(
        _t(
            "You need to start Odoo with at least two workers to print a pdf version of the reports."
        )
    );
    await animationFrame();
    const text = queryText(".o_notification_content");
    expect(text).toMatch(/Viindoo/);
    expect(text).not.toInclude("Odoo");
});

test("another notification is shown unchanged", async () => {
    await mountNotifications();
    getService(NotificationPlugin).add("Some other message");
    await animationFrame();
    expect(".o_notification_content").toHaveText("Some other message");
});
