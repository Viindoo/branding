import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { user } from "@web/core/user";

patch(WebClient.prototype, {
    /**
     * @override
     */
    setup() {
        super.setup();
        this.user = user;
        // Update Favicons
        // This patches the core WebClient, which is also mounted by bare
        // test envs where the user session carries no active company.
        // Degrade gracefully (skip the favicon update) instead of crashing
        // every WebClient test; production always has an active company.
        const currentCompany = this.user.activeCompanies?.[0];
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
