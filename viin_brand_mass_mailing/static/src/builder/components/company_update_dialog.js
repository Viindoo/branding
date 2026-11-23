import { patch } from "@web/core/utils/patch";
import { ResCompanyUpdateDialog } from "@mass_mailing/builder/components/company_update_dialog";
import { VIINDOO_SOCIAL_LINKS } from "@viin_brand/core/social_links/viindoo_social_links";

patch(ResCompanyUpdateDialog.prototype, {
    setup() {
        super.setup(...arguments);
        this.fieldNames = this.fieldNames.map((field) => ({
            ...field,
            placeholder: VIINDOO_SOCIAL_LINKS[field.name] ?? field.placeholder,
        }));
    },
});
