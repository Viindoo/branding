import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";

describe.current.tags("headless");

test("the SMS field links to no page of Odoo", () => {
    const template = getTemplate("sms.SmsWidget");
    expect(template.querySelectorAll("a[href*='odoo.com']")).toHaveLength(0);
    expect(template.querySelectorAll(".o_sms_count")).toHaveLength(1);
});
