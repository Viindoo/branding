import { describe, expect, test } from "@odoo/hoot";
import { registry } from "@web/core/registry";
import { getTemplate } from "@web/core/templates";
import { DEFAULT_FACEBOOK_PAGE } from "@viin_brand_website/builder/plugins/options/facebook_option_plugin";

describe.current.tags("headless");

const BRAND_NAME = /\bOdoo\b|odoo\.com/i;

function serialize(name) {
    const template = getTemplate(name);
    return template.outerHTML ?? new XMLSerializer().serializeToString(template);
}

function facebookPlugin(socialFacebook) {
    const Plugin = registry.category("website-plugins").get("facebookOption");
    const plugin = Object.create(Plugin.prototype);
    plugin.services = {
        orm: { read: async () => [{ social_facebook: socialFacebook }] },
        website: { currentWebsite: { id: 1 } },
    };
    plugin.dependencies = { history: { ignoreDOMMutations: (callback) => callback() } };
    plugin.config = { onChange() {} };
    plugin.dispatchTo = () => {};
    const editable = document.createElement("div");
    const node = document.createElement("div");
    node.className = "o_facebook_page";
    editable.append(node);
    plugin.editable = editable;
    return { plugin, node };
}

test("the Instagram option tooltip names Viindoo", () => {
    const html = serialize("website.InstagramOption");
    expect(html).not.toMatch(BRAND_NAME);
    expect(html).toInclude("Viindoo website");
});

test("the mega menu option offers the Viindoo menu", () => {
    const html = serialize("website.MegaMenuOption");
    expect(html).not.toMatch(BRAND_NAME);
    expect(html).toInclude("Viindoo Menu");
});

test("the countdown end message names no brand", () => {
    const html = serialize("website.s_countdown.end_message");
    expect(html).not.toMatch(BRAND_NAME);
    expect(html).toInclude("Happy Anniversary!");
    expect(html).not.toInclude("Viindoo");
});

test("the Google font help is not a link to odoo.com", () => {
    const html = serialize("website.dialog.addFont");
    expect(html).not.toMatch(BRAND_NAME);
});

test("a Facebook block without a page falls back to the Viindoo page", async () => {
    const { plugin, node } = facebookPlugin(false);
    await plugin.loadAndSetEmptyLink([node]);
    expect(node.dataset.href).toBe(DEFAULT_FACEBOOK_PAGE);
    expect(DEFAULT_FACEBOOK_PAGE).toBe("https://www.facebook.com/Viindoo");
});

test("a Facebook block uses the Facebook page the website already declares", async () => {
    const { plugin, node } = facebookPlugin("https://www.facebook.com/AcmeShop");
    await plugin.loadAndSetEmptyLink([node]);
    expect(node.dataset.href).toBe("https://www.facebook.com/AcmeShop");
});
