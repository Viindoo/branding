import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";
import { registry } from "@web/core/registry";
import { iapNotificationService } from "@iap_mail/js/services/iap_notification_service";
import "@viin_brand_iap/action_buttons_widget/no_credits_widget";
import "@viin_brand_iap/services/iap_notification_service";

describe.current.tags("headless");

test("the buy-credits widget of a settings row renders nothing", () => {
    const { component } = registry.category("view_widgets").get("iap_buy_more_credits");
    const template = getTemplate(component.template);
    expect(component.template).toBe("viin_brand_iap.NoCreditsWidget");
    expect(template.querySelectorAll("button, a")).toHaveLength(0);
    expect(template.textContent.trim()).toBe("");
});

test("a service out of credits is announced without a link to buy credits", () => {
    const callbacks = [];
    const notifications = [];
    iapNotificationService.start(
        {},
        {
            bus_service: { subscribe: (name, callback) => callbacks.push(callback), start() {} },
            notification: { add: (message, options) => notifications.push({ message, options }) },
        }
    );
    callbacks[0]({
        type: "no_credit",
        title: "Not enough credits",
        get_credits_url: "https://iap.odoo.com/iap/1/credit",
    });
    expect(notifications).toHaveLength(1);
    expect(String(notifications[0].message)).not.toInclude("href");
    expect(String(notifications[0].message)).not.toInclude("odoo.com");
    expect(notifications[0].options.type).toBe("danger");
});
