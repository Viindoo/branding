import { describe, expect, test } from "@odoo/hoot";
import { queryAllAttributes, queryAllTexts, queryOne } from "@odoo/hoot-dom";
import {
    contains,
    defineModels,
    fields,
    models,
    mountWithCleanup,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { defineCrmModels } from "@crm/../tests/crm_test_helpers";
import {
    LeadGenerationDropdown,
    MODULE_STATUS,
} from "@crm/components/lead_generation_dropdown/lead_generation_dropdown";
import "@viin_brand_crm/components/lead_generation_dropdown/lead_generation_dropdown";

describe.current.tags("desktop");

const ODOO_HOST = /(^|\.)odoo(cdn)?\.com$/i;

class IrModuleModule extends models.Model {
    _name = "ir.module.module";

    name = fields.Char();
    shortdesc = fields.Char();

    _records = [
        { id: 1, name: "crm_iap_mine", shortdesc: "Lead Mining" },
        { id: 2, name: "website", shortdesc: "Website" },
        { id: 3, name: "mass_mailing", shortdesc: "Email Marketing" },
        { id: 4, name: "survey", shortdesc: "Surveys" },
    ];
}

defineCrmModels();
defineModels([IrModuleModule]);

async function openGenerateMenu() {
    await mountWithCleanup(LeadGenerationDropdown, {
        env: { searchModel: { context: {}, resModel: "crm.lead" } },
    });
    await contains("button:contains(Generate)").click();
    return queryAllAttributes(".o_lead_mining_element", "data-module-xml-id");
}

test("the Generate menu keeps the app installs, Mail plugins and the import, and drops Lead Sourcing", async () => {
    const entries = await openGenerateMenu();

    expect(entries).toInclude("base.module_website");
    expect(entries).toInclude("base.module_mass_mailing");
    expect(entries).toInclude("base.module_survey");
    expect(entries).toInclude("not_a_module");
    expect(entries).toInclude("base.module_crm");
    expect(entries).not.toInclude("base.module_crm_iap_mine");
});

test("the Mail plugins entry opens a dialog that names Viindoo and carries no Odoo mark", async () => {
    await openGenerateMenu();
    await contains(".o_lead_mining_element[data-module-xml-id='not_a_module']").click();

    const dialog = queryOne(".modal");
    const text = queryAllTexts(".modal").join(" ");
    expect(text).toMatch(/\bViindoo\b/);
    expect(text).not.toMatch(/\bOdoo\b/i);
    const urls = [
        ...queryAllAttributes(".modal [src]", "src"),
        ...queryAllAttributes(".modal [href]", "href"),
    ].map((url) => new URL(url, window.location.href));
    for (const url of urls) {
        expect(ODOO_HOST.test(url.hostname)).toBe(false, { message: url.href });
    }
    for (const image of dialog.querySelectorAll("img")) {
        expect(new URL(image.getAttribute("src"), window.location.href).origin).toBe(
            window.location.origin,
            { message: "the images of the dialog are served by this database" }
        );
    }
});

test("the Lead Sourcing entry that the lead mining module completes stays out of the menu", async () => {
    patchWithCleanup(LeadGenerationDropdown.prototype, {
        setup() {
            super.setup();
            const miningEntry = this.state.dropdownContentElements.find(
                (element) => element.moduleXmlId === "base.module_crm_iap_mine"
            );
            Object.assign(miningEntry, { status: MODULE_STATUS.INSTALLED, onClick: () => {} });
        },
    });

    const entries = await openGenerateMenu();

    expect(entries).not.toInclude("base.module_crm_iap_mine");
    expect(entries).toInclude("base.module_website");
});
