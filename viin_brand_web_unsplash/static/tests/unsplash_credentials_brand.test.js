import { describe, expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";

describe.current.tags("headless");

test("the Unsplash credentials links lead to Viindoo documentation, not to Odoo", () => {
    const links = [...getTemplate("web_unsplash.UnsplashCredentials").querySelectorAll("a")];

    expect(links.length).toBeGreaterThan(0);
    for (const link of links) {
        expect(new URL(link.getAttribute("href")).hostname).toBe("viindoo.com");
    }
});
