import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";

describe.current.tags("headless");

test("the kiosk is powered by the Viindoo logo", () => {
    const template = getTemplate("hr_attendance.public_kiosk_app");
    const logos = template.querySelectorAll("img[src$='Viindoo-logo.svg']");
    expect(logos).toHaveLength(2);
    for (const logo of logos) {
        expect(logo.getAttribute("alt")).toBe("Viindoo Logo");
    }
    expect(
        template.querySelectorAll("img[alt*='Odoo'], img[src='/web/static/img/logo.png']")
    ).toHaveLength(0);
});
