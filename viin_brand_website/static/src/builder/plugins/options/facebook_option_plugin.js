import "@website/builder/plugins/options/facebook_option_plugin";
import { getCommonAncestor } from "@html_editor/utils/dom_traversal";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

export const DEFAULT_FACEBOOK_PAGE = "https://www.facebook.com/Viindoo";

const FacebookOptionPlugin = registry.category("website-plugins").get("facebookOption");

patch(FacebookOptionPlugin.prototype, {
    /**
     * Fill the Facebook blocks that have no page yet with the website's own Facebook page,
     * falling back to the Viindoo page.
     *
     * Mirrors `loadAndSetEmptyLink` of the core plugin: its fallback page is a literal inside the
     * method, so the method is re-declared here.
     */
    async loadAndSetEmptyLink(nodes) {
        if (this.facebookUrl) {
            this.setEmptyLink(nodes);
            return;
        }
        const res = await this.services.orm.read(
            "website",
            [this.services.website.currentWebsite.id],
            ["social_facebook"]
        );
        if (res) {
            this.facebookUrl = res[0].social_facebook || DEFAULT_FACEBOOK_PAGE;
            const hasChanged = this.dependencies.history.ignoreDOMMutations(() =>
                this.setEmptyLink(nodes)
            );
            if (hasChanged) {
                const commonAncestor = getCommonAncestor(nodes, this.editable);
                this.dispatchTo("content_manually_updated_handlers", commonAncestor);
                this.config.onChange({ isPreviewing: false });
            }
        }
    },
});
