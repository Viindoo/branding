import { describe, expect, test } from "@odoo/hoot";
import { registry } from "@web/core/registry";
import { getTemplate } from "@web/core/templates";
import { VIINDOO_SOCIAL_LINKS } from "@viin_brand/core/social_links/viindoo_social_links";

describe.current.tags("headless");

const BRAND_NAME = /\bOdoo\b|odoo\.com/i;

function serialize(name) {
    const template = getTemplate(name);
    return template.outerHTML ?? new XMLSerializer().serializeToString(template);
}

function facebookPlugin(socialFacebook) {
    const Plugin = registry.category("website-plugins").get("facebookOption");
    const plugin = Object.create(Plugin.prototype);
    const calls = { ignore: 0, onChange: [], triggered: [] };
    plugin.services = {
        orm: { read: async () => [{ social_facebook: socialFacebook }] },
        website: { currentWebsite: { company_id: 1 } },
    };
    plugin.dependencies = {
        domObserver: {
            ignore(callback) {
                calls.ignore++;
                return callback();
            },
        },
    };
    plugin.config = { onChange: (params) => calls.onChange.push(params) };
    plugin.trigger = (name, ...args) => calls.triggered.push([name, ...args]);
    plugin.editable = document.createElement("div");
    const node = document.createElement("div");
    node.className = "o_facebook_page";
    plugin.editable.append(node);
    return { plugin, node, calls };
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
    expect(html).not.toInclude("Viindoo");
});

test("the Google font help is not a link to odoo.com", () => {
    const html = serialize("website.dialog.addFont");
    expect(html).not.toMatch(BRAND_NAME);
});

test("the form file size tooltip does not name the hosting of Odoo", () => {
    const html = serialize("website.s_website_form_field_option");
    expect(html).not.toMatch(BRAND_NAME);
});

test("the SEO keywords help offers no link to the documentation of Odoo", () => {
    const html = serialize("website.seoMetaKeywordsDocumentationLink");
    expect(html).not.toMatch(BRAND_NAME);
});

test("the resource editor warning links nowhere to odoo.com", () => {
    const html = serialize("website.ResourceEditorWarningOverlay");
    expect(html).not.toMatch(BRAND_NAME);
});

test("a Facebook block without a page falls back to the Viindoo page", async () => {
    const { plugin, node } = facebookPlugin(false);
    await plugin.loadAndSetEmptyLink([node]);
    expect(node.dataset.href).toBe(VIINDOO_SOCIAL_LINKS.social_facebook);
});

test("a Facebook block uses the Facebook page the company already declares", async () => {
    const { plugin, node } = facebookPlugin("https://www.facebook.com/AcmeShop");
    await plugin.loadAndSetEmptyLink([node]);
    expect(node.dataset.href).toBe("https://www.facebook.com/AcmeShop");
});

test("the first fill of a Facebook block goes through the observer and notifies the editor once", async () => {
    const { plugin, node, calls } = facebookPlugin(false);
    await plugin.loadAndSetEmptyLink([node]);
    expect(calls.ignore).toBe(1);
    expect(calls.triggered.map(([name]) => name)).toEqual(["on_content_manually_updated_handlers"]);
    expect(calls.onChange).toEqual([{ isPreviewing: false }]);
});

test("the company is read once for all the Facebook blocks of a page", async () => {
    const { plugin, node } = facebookPlugin(false);
    let reads = 0;
    plugin.services.orm.read = async () => {
        reads++;
        return [{ social_facebook: false }];
    };
    const other = document.createElement("div");
    other.className = "o_facebook_page";
    await plugin.loadAndSetEmptyLink([node]);
    await plugin.loadAndSetEmptyLink([other]);
    expect(reads).toBe(1);
    expect(other.dataset.href).toBe(VIINDOO_SOCIAL_LINKS.social_facebook);
});
