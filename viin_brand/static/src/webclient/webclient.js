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
        // Bare test environments mount WebClient without an active company: skip the favicon
        // update there instead of crashing.
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
