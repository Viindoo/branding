import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";
import { registry } from "@web/core/registry";
import { mountWithCleanup } from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { iapNotificationService } from "@iap_mail/js/services/iap_notification_service";
import "@viin_brand_iap/action_buttons_widget/no_credits_widget";
import "@viin_brand_iap/services/iap_notification_service";

describe.current.tags("desktop");

defineMailModels();

function startNotificationService() {
    const callbacks = [];
    const notifications = [];
    iapNotificationService.start(
        {},
        {
            bus_service: { subscribe: (name, callback) => callbacks.push(callback), start() {} },
            notification: { add: (message, options) => notifications.push({ message, options }) },
        }
    );
    return { callbacks, notifications };
}

test("the buy-credits widget of a settings row renders nothing once mounted", async () => {
    const { component } = registry.category("view_widgets").get("iap_buy_more_credits");
    await mountWithCleanup(component, { props: { record: {}, readonly: false } });
    expect("button, a").toHaveCount(0);
    expect(getTemplate(component.template).textContent.trim()).toBe("");
});

test("a service out of credits is announced without a way to buy credits", () => {
    const { callbacks, notifications } = startNotificationService();
    callbacks[0]({
        type: "no_credit",
        title: "Not enough credits",
        get_credits_url: "https://iap.odoo.com/iap/1/credit",
    });
    expect(notifications).toHaveLength(1);
    expect(String(notifications[0].message)).toBe("Not enough credits");
    expect(String(notifications[0].message)).not.toInclude("odoo.com");
    expect(notifications[0].options.type).toBe("danger");
    expect(notifications[0].options.buttons).toHaveLength(0);
});

test("the other notifications of a service are announced as core builds them", () => {
    const { callbacks, notifications } = startNotificationService();
    callbacks[0]({ type: "success", title: "Done", message: "Account updated" });
    expect(notifications).toHaveLength(1);
    expect(String(notifications[0].message)).toBe("Account updated");
    expect(notifications[0].options.title).toBe("Done");
    expect(notifications[0].options.type).toBe("success");
});
