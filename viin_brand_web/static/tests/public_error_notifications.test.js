import { expect, test } from "@odoo/hoot";
import { patchTranslations } from "@web/../tests/web_test_helpers";
import { registry } from "@web/core/registry";

const SESSION_EXPIRED_KEYS = ["odoo.http.SessionExpiredException", "werkzeug.exceptions.Forbidden"];

for (const key of SESSION_EXPIRED_KEYS) {
    test(`the public notification of ${key} reads the Viindoo brand, not Odoo`, () => {
        patchTranslations();
        const notification = registry.category("error_notifications").get(key);

        expect(notification.title.toString()).toMatch(/Viindoo/);
        expect(notification.title.toString()).not.toMatch(/Odoo/);
        expect(notification.message.toString()).toMatch(/Viindoo/);
        expect(notification.message.toString()).not.toMatch(/Odoo/);
    });
}
