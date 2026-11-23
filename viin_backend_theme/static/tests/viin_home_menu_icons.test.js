import { animationFrame, describe, expect, test } from "@odoo/hoot";
import { queryAll, queryOne } from "@odoo/hoot-dom";
import { registry } from "@web/core/registry";
import {
    defineMenus,
    defineModels,
    fields,
    mountWithCleanup,
    onRpc,
} from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";
import { getAppIconUrl } from "@viin_backend_theme/webclient/app_icons";

// A tile shows the icon its app declares: the Viindoo image when one exists for the app's module,
// the image the server sent otherwise, and the glyph of a built icon (`<icon name>,<color>,<background>`)
// which has no image at all.

class ResUsers extends mailModels.ResUsers {
    viin_home_app_order = fields.Char();
}
defineModels({ ...mailModels, ResUsers });

const IMAGE_OF_THE_SERVER = "data:image/png;base64,iVBORw0KGgo=";

defineMenus([
    {
        id: 1,
        appID: 1,
        name: "Sales",
        xmlid: "app.sales",
        webIcon: "sale,static/description/icon.png",
        webIconData: IMAGE_OF_THE_SERVER,
    },
    {
        id: 2,
        appID: 2,
        name: "Third Party",
        xmlid: "app.third_party",
        webIcon: "some_third_party_module,static/description/icon.png",
        webIconData: IMAGE_OF_THE_SERVER,
    },
    {
        id: 3,
        appID: 3,
        name: "Glyph",
        xmlid: "app.glyph",
        webIcon: "apps,#FFFFFF,#7F4282",
    },
]);

async function mountHomeMenu() {
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
    await mountWithCleanup(registry.category("actions").get("viin_home_menu"));
    await animationFrame();
}

function tile(xmlid) {
    return queryOne(`.o_viin_home_app[data-menu-xmlid='${xmlid}']`);
}

describe("home menu tile icons", () => {
    // The test harness swaps every <img> source for its own placeholder, so the source an app is
    // given is read from the resolver the tile uses.
    test("an app whose module has a Viindoo icon gets that icon", () => {
        expect(
            getAppIconUrl({
                webIcon: "sale,static/description/icon.png",
                webIconData: IMAGE_OF_THE_SERVER,
            })
        ).toBe("/viin_brand/static/img/apps/sale.png");
    });

    test("an app without a Viindoo icon gets the image the server sent", () => {
        expect(
            getAppIconUrl({
                webIcon: "some_third_party_module,static/description/icon.png",
                webIconData: IMAGE_OF_THE_SERVER,
            })
        ).toBe(IMAGE_OF_THE_SERVER);
    });

    test("a built icon never borrows the Viindoo icon of a module named like its glyph", () => {
        expect(getAppIconUrl({ webIcon: "sale,#FFFFFF,#7F4282" })).toBe(
            "/web/static/img/default_icon_app.png"
        );
    });

    test("a built icon is drawn as its glyph on its own background, with no image", async () => {
        await mountHomeMenu();
        const glyph = tile("app.glyph").querySelector("i.oi");
        expect(glyph).toHaveAttribute("data-icon", "apps");
        expect(glyph).toHaveStyle({
            color: "rgb(255, 255, 255)",
            backgroundColor: "rgb(127, 66, 130)",
        });
        expect(tile("app.glyph").querySelectorAll("img")).toHaveLength(0);
        expect(tile("app.sales").querySelectorAll("i.oi")).toHaveLength(0);
        expect(queryAll(".o_viin_home_app")).toHaveLength(3);
    });
});
