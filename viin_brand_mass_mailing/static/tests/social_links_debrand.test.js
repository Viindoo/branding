import { describe, expect, test } from "@odoo/hoot";
import { queryAll } from "@odoo/hoot-dom";
import { defineMailModels, mailModels } from "@mail/../tests/mail_test_helpers";
import {
    assignDialogTestEnv,
    defineModels,
    fields,
    models,
    mountWithCleanup,
} from "@web/../tests/web_test_helpers";
import { renderToFragment } from "@web/core/utils/render";
import { MassMailingSocialMediaOptionPlugin } from "@mass_mailing/builder/plugins/social_media_option_plugin";
import { ResCompanyUpdateDialog } from "@mass_mailing/builder/components/company_update_dialog";
import { VIINDOO_SOCIAL_LINKS } from "@viin_brand/core/social_links/viindoo_social_links";
import "@viin_brand_mass_mailing/builder/components/company_update_dialog";
import "@viin_brand_mass_mailing/builder/plugins/social_media_option_plugin";

class ResCompany extends models.Model {
    _name = "res.company";

    name = fields.Char();
    social_twitter = fields.Char();
    social_facebook = fields.Char();
    social_github = fields.Char();
    social_linkedin = fields.Char();
    social_youtube = fields.Char();
    social_instagram = fields.Char();
    social_tiktok = fields.Char();
    social_discord = fields.Char();

    _records = mailModels.ResCompany._records;
}

defineMailModels();
defineModels([ResCompany]);

describe.current.tags("desktop");

const BRAND_NAME = /odoo|openerp/i;

const renderedLinks = (socialLinks) => {
    const block = renderToFragment("mass_mailing.social_links", {
        company_id: { id: 1, social_links: socialLinks },
        fillSocialLinks: true,
    });
    return Object.fromEntries(
        [...block.querySelectorAll("a[data-platform]")].map((link) => [
            link.dataset.platform.replace("customLink-", ""),
            link.getAttribute("href"),
        ])
    );
};

test("the social block of the builder links to Viindoo when the company has no account", () => {
    const links = renderedLinks({});

    expect(Object.keys(links)).toEqual([
        "social_facebook",
        "social_instagram",
        "social_twitter",
        "social_linkedin",
        "social_tiktok",
        "social_youtube",
    ]);
    for (const [network, href] of Object.entries(links)) {
        expect(href).toBe(VIINDOO_SOCIAL_LINKS[network]);
        expect(href).not.toMatch(BRAND_NAME);
    }
});

test("the social block of the builder keeps the account of the company", () => {
    const links = renderedLinks({ social_facebook: "https://www.facebook.com/our.company" });

    expect(links.social_facebook).toBe("https://www.facebook.com/our.company");
    expect(links.social_linkedin).toBe(VIINDOO_SOCIAL_LINKS.social_linkedin);
});

test("the links added for a user who cannot edit the company are Viindoo's", () => {
    const values = Reflect.get(MassMailingSocialMediaOptionPlugin.prototype, "baseMediaValues", {});

    expect(Object.keys(values).length).toBeGreaterThan(0);
    for (const [platform, href] of Object.entries(values)) {
        expect(href).toBe(VIINDOO_SOCIAL_LINKS[`social_${platform}`]);
    }
});

test("the account fields of the company dialog suggest Viindoo's accounts", async () => {
    assignDialogTestEnv();
    await mountWithCleanup(ResCompanyUpdateDialog, { props: { resId: 1, close: () => {} } });

    const placeholders = Object.fromEntries(
        queryAll("input[name^='social_']").map((input) => [
            input.getAttribute("name"),
            input.getAttribute("placeholder"),
        ])
    );
    for (const [network, href] of Object.entries(VIINDOO_SOCIAL_LINKS)) {
        expect(placeholders[network]).toBe(`e.g. ${href}`);
    }
    for (const placeholder of Object.values(placeholders)) {
        expect(placeholder).not.toMatch(BRAND_NAME);
    }
});
