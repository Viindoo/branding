# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Load the real public pages in a browser: a template extension is applied lazily at mount time,
so a bundle that merely compiles (test_bundle_compile) can still render a blank page."""
import json

from odoo.tests.common import HttpCase, tagged
from odoo.tools.translate import code_translations

from .common import activate_frontend_lang

# viewBox of the Viindoo logo shipped by viin_brand_pos (core's Odoo logo is "0 0 919 495").
VIINDOO_LOGO_VIEWBOX = "0 0 850 201"
# msgid of a term this module ships to the customer display (iot_notice.js)
IOT_NOTICE = ("Make sure the IoT Box is switched on and connected to the network, "
              "then restart the IoT Box.")


@tagged("post_install", "-at_install")
class TestCustomerDisplayRender(HttpCase):

    def test_customer_display_renders_viindoo_logo_without_and_with_an_order(self):
        config = self.env["pos.config"].create({"name": "Customer display shop"})
        url = "/pos_customer_display/%s/test-device?access_token=%s" % (config.id, config.access_token)
        code = """
            (async () => {
                const wait = async (condition, label) => {
                    for (let i = 0; i < 150; i++) {
                        if (condition()) {
                            return;
                        }
                        await new Promise((resolve) => setTimeout(resolve, 100));
                    }
                    throw new Error("timeout waiting for: " + label);
                };
                const logos = () =>
                    [...document.querySelectorAll(".o_customer_display svg")].map((s) => s.getAttribute("viewBox"));
                const assertViindooLogos = (state) => {
                    if (!logos().length) {
                        throw new Error(state + ": no Powered by logo rendered");
                    }
                    for (const viewBox of logos()) {
                        if (viewBox !== "%(viindoo)s") {
                            throw new Error(state + ": unexpected logo " + viewBox);
                        }
                    }
                };

                // empty-order state
                await wait(() => document.querySelector(".o_customer_display"), "customer display mounted");
                assertViindooLogos("empty order");

                // with-order state, fed the way the POS cashier screen feeds it
                new BroadcastChannel("UPDATE_CUSTOMER_DISPLAY").postMessage({
                    finalized: false, general_customer_note: "", amount: "$ 10.00", subtotal: false,
                    amountTaxes: false, change: false, paymentLines: [],
                    lines: [{
                        productId: 1, taxGroupLabels: [], discount: "", customerNote: "", internalNote: "[]",
                        productName: "Chair", price: "$ 10.00", qty: "1", unit: "Units", unitPrice: "$ 10.00",
                        packLotLines: [], comboParent: "", price_without_discount: "$ 10.00", isSelected: true,
                    }],
                });
                await wait(() => document.querySelector(".o_customer_display .orderline"), "order line rendered");
                assertViindooLogos("with order");
                console.log("test successful");
            })().catch((error) => console.error(error.message));
        """ % {"viindoo": VIINDOO_LOGO_VIEWBOX}
        self.browser_js(url, code, timeout=120)

    def test_customer_display_serves_this_module_terms_in_the_visitor_language(self):
        """A logged-out Vietnamese visitor gets this module's terms in Vietnamese."""
        activate_frontend_lang(self.env, "vi_VN")
        expected = next(
            (m["string"] for m in code_translations.get_web_translations("viin_brand_pos", "vi_VN")["messages"]
             if m["id"] == IOT_NOTICE),
            None,
        )
        self.assertTrue(expected and expected != IOT_NOTICE, "vi_VN.po must translate the IoT notice")
        config = self.env["pos.config"].create({"name": "Customer display shop"})
        url = "/pos_customer_display/%s/test-device?access_token=%s" % (config.id, config.access_token)
        code = """
            (async () => {
                for (let i = 0; i < 150 && !document.querySelector(".o_customer_display"); i++) {
                    await new Promise((resolve) => setTimeout(resolve, 100));
                }
                if (!document.querySelector(".o_customer_display")) {
                    throw new Error("the customer display did not mount");
                }
                const { _t } = odoo.loader.modules.get("@web/core/l10n/translation");
                const got = String(_t(%(msgid)s));
                if (got !== %(expected)s) {
                    throw new Error("not translated for the visitor: " + got);
                }
                console.log("test successful");
            })().catch((error) => console.error(error.message));
        """ % {"msgid": json.dumps(IOT_NOTICE), "expected": json.dumps(expected)}
        self.browser_js(url, code, cookies={"frontend_lang": "vi_VN"}, timeout=120)
