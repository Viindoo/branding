import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import "@viin_brand/views/widgets/documentation_link/documentation_link";

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

test("the installation manual of the kiosk opens a Viindoo page", () => {
    const url = Reflect.get(DocumentationLink.prototype, "url", {
        props: { path: "/applications/hr/attendances/hardware.html" },
    });

    expect(new URL(url).hostname).toBe("viindoo.com");
});
