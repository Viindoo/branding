import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class IapNoCreditsWidget extends Component {
    static template = "viin_brand_iap.NoCreditsWidget";
    static props = ["*"];
}

registry
    .category("view_widgets")
    .add("iap_buy_more_credits", { component: IapNoCreditsWidget }, { force: true });
