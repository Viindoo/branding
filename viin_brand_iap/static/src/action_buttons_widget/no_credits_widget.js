import { Component, useProps } from "@odoo/owl";
import "@iap/action_buttons_widget/action_buttons_widget";
import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

class IapNoCreditsWidget extends Component {
    static template = "viin_brand_iap.NoCreditsWidget";
    props = useProps({ ...standardWidgetProps });
}

// Core registers its own widget under this name without `force`, so it is imported first.
registry
    .category("view_widgets")
    .add("iap_buy_more_credits", { component: IapNoCreditsWidget }, { force: true });
