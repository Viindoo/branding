import { FacebookOptionPlugin } from "@website/builder/plugins/options/facebook_option_plugin";
import { getCommonAncestor } from "@html_editor/utils/dom_traversal";
import { VIINDOO_SOCIAL_LINKS } from "@viin_brand/core/social_links/viindoo_social_links";
import { patch } from "@web/core/utils/patch";

patch(FacebookOptionPlugin.prototype, {
    /**
     * A Facebook block without a page takes the Facebook page of the website's company, else the
     * Viindoo page, in place of the Odoo page core falls back to. The first fill goes through the
     * same observer and notification path as core's own first fill.
     */
    async loadAndSetEmptyLink(nodes) {
        if (this.facebookUrl) {
            return super.loadAndSetEmptyLink(nodes);
        }
        const [company] = await this.services.orm.read(
            "res.company",
            [this.services.website.currentWebsite.company_id],
            ["social_facebook"]
        );
        this.facebookUrl = company?.social_facebook || VIINDOO_SOCIAL_LINKS.social_facebook;
        const hasChanged = this.dependencies.domObserver.ignore(() => this.setEmptyLink(nodes));
        if (hasChanged) {
            const commonAncestor = getCommonAncestor(nodes, this.editable);
            this.trigger("on_content_manually_updated_handlers", commonAncestor);
            this.config.onChange({ isPreviewing: false });
        }
    },
});
