import { patch } from "@web/core/utils/patch";
import { MassMailingSocialMediaOptionPlugin } from "@mass_mailing/builder/plugins/social_media_option_plugin";
import { VIINDOO_SOCIAL_LINKS } from "@viin_brand/core/social_links/viindoo_social_links";

patch(MassMailingSocialMediaOptionPlugin.prototype, {
    get baseMediaValues() {
        return Object.fromEntries(
            Object.keys(super.baseMediaValues).map((platform) => [
                platform,
                VIINDOO_SOCIAL_LINKS[`social_${platform}`],
            ])
        );
    },
});
