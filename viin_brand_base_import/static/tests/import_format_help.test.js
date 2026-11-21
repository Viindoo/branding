import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { allowTranslations } from "@web/../tests/web_test_helpers";
import { BaseImportModel } from "@base_import/import_model";
import "@viin_brand_base_import/import_model";

describe.current.tags("headless");

beforeEach(() => {
    allowTranslations();
});

test("the date and datetime format help of the import options do not name Odoo", () => {
    const options = BaseImportModel.prototype._getCSVFormattingOptions.call({});

    for (const name of ["date_format", "datetime_format"]) {
        expect(options[name].help).not.toInclude("Odoo");
        expect(options[name].help).toInclude("Viindoo");
    }
});
