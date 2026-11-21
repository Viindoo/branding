import { BaseImportModel } from "@base_import/import_model";
import { patch } from "@web/core/utils/patch";

patch(BaseImportModel.prototype, {
    _getCSVFormattingOptions() {
        const options = super._getCSVFormattingOptions(...arguments);
        // Core's text names its own product; the sentence is replaced in whatever language it is.
        for (const name of ["date_format", "datetime_format"]) {
            options[name].help = options[name].help.replace(/\bOdoo\b/g, "Viindoo");
        }
        return options;
    },
});
