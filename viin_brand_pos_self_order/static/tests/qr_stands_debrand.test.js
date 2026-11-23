import { expect, test } from "@odoo/hoot";
import { getTemplate } from "@web/core/templates";

test("the burger menu offers no QR code order from a page of another vendor", () => {
    const html = getTemplate("point_of_sale.BurgerMenuDialog").outerHTML;

    expect(html).not.toInclude("redirectToQrForm");
    expect(html).toInclude("install-app");
});

test("the floor screen offers no QR code order from a page of another vendor", () => {
    const html = getTemplate("pos_restaurant.FloorScreen").outerHTML;

    expect(html).not.toInclude("qr-order-button");
    expect(html).toInclude("button-table-selector");
});
