import { patch } from "@web/core/utils/patch";
import { LeadGenerationDropdown } from "@crm/components/lead_generation_dropdown/lead_generation_dropdown";

// Lead Sourcing is a paid service of Odoo. The other entries install an app of the Community Edition,
// open the Mail plugins dialog or import leads.
const HIDDEN_MODULE_XML_IDS = new Set(["base.module_crm_iap_mine"]);

patch(LeadGenerationDropdown.prototype, {
    // The entries are filtered where the menu reads them: the Lead Sourcing entry is completed by
    // the module that provides the service, whichever of the two modules is set up first.
    get sortedDropdownContentElements() {
        return super.sortedDropdownContentElements.filter(
            (element) => !HIDDEN_MODULE_XML_IDS.has(element.moduleXmlId)
        );
    },
});
