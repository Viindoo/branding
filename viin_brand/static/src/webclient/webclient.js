import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

patch(WebClient.prototype, {
    /**
     * @override
     */
    setup() {
        super.setup();
        // Update Favicons
        // This patches the core WebClient, which is also mounted by the bare
        // `web` QUnit env where the company service is not started. Degrade
        // gracefully (skip the favicon update) instead of crashing every
        // WebClient test; production always has the service.
        const currentCompany = this.env.services.company?.currentCompany;
        if (!currentCompany) {
            return;
        }
        const favicon = `/web/image/res.company/${currentCompany.id}/favicon`;
        const icons = document.querySelectorAll("link[rel*='icon']");
        for (const icon of icons) {
            if (icon.rel != "apple-touch-icon") {
                icon.href = favicon;
            }
        }
    },
});
