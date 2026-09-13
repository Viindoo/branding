import { SettingsPage } from "@web/webclient/settings_form_view/settings/settings_page"
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { useEffect } from "@odoo/owl";

patch(SettingsPage.prototype, {
    setup() {
        super.setup();
        this.state.modules = this.props.modules;
        const self = this;
        useEffect(
            () => {
                // Server-stamped session marker (see viin_brand ir_http): only
                // genuine webclient sessions fetch the brand module icons.
                // QUnit environments (mock session, key absent) skip the RPC,
                // keeping core SettingsFormView request assertions clean
                // (runbot 223235/396399).
                if (!session.viin_brand_settings_icons) {
                    return;
                }
                self.env.model.orm
                    .call("res.config.settings", "get_viin_brand_modules_icon", [], {
                        modules: self.props.modules.map((m) => m.key),
                    })
                    .then((res) => {
                        if (res && res.length > 0) {
                            const modules = [...self.props.modules];
                            modules.forEach((child, index) => {
                                child.imgurl = res[index];
                            });
                            self.state.modules = modules;
                        }
                    });
            },
            () => []
        );
    },
});
