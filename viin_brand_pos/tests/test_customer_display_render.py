# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Load the real public pages in a browser: a template extension is applied lazily at mount time,
so a bundle that merely compiles (test_bundle_compile) can still render a blank page."""
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCustomerDisplayRender(HttpCase):

    def _display_url(self):
        config = self.env["pos.config"].create({"name": "Customer display shop"})
        return "/pos_customer_display/%s/test-device?access_token=%s" % (config.id, config.access_token)

    def test_customer_display_shows_the_viindoo_logo_and_title_in_every_state(self):
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
                const footerLogos = () =>
                    [...document.querySelectorAll(".o_customer_display svg")].map((s) => s.getAttribute("viewBox"));
                const assertViindooFooter = (state) => {
                    if (!footerLogos().length) {
                        throw new Error(state + ": no Powered by logo rendered");
                    }
                    for (const viewBox of footerLogos()) {
                        if (viewBox !== "%(viindoo)s") {
                            throw new Error(state + ": unexpected logo " + viewBox);
                        }
                    }
                };

                // waiting for an order
                await wait(() => document.querySelector(".o_customer_display"), "customer display mounted");
                assertViindooFooter("waiting for an order");
                if (/odoo/i.test(document.title)) {
                    throw new Error("the tab title names Odoo: " + document.title);
                }

                // the idle screen, fed the way the POS cashier screen feeds it
                odoo.__WOWL_DEBUG__.root.customerDisplay.data.set({ displayScreenSaver: true });
                await wait(() => document.querySelector(".login-overlay .pos-logo"), "idle screen");
                const image = getComputedStyle(document.querySelector(".login-overlay .pos-logo")).backgroundImage;
                if (!image.includes("viin_brand_pos") || !image.includes("viindoo-logo")) {
                    throw new Error("the idle screen logo is not the Viindoo one: " + image);
                }
                console.log("test successful");
            })().catch((error) => console.error(error.message));
        """ % {"viindoo": "0 0 850 201"}  # viewBox of the Viindoo logo; core's Odoo logo is "0 0 919 495"
        self.browser_js(self._display_url(), code, timeout=120)

    def test_customer_display_error_dialogs_do_not_name_odoo(self):
        """The customer display bundle (web._assets_core only) gets the error-dialog de-brand."""
        code = """
            (async () => {
                for (let i = 0; i < 150 && !document.querySelector(".o_customer_display"); i++) {
                    await new Promise((resolve) => setTimeout(resolve, 100));
                }
                if (!document.querySelector(".o_customer_display")) {
                    throw new Error("the customer display did not mount");
                }
                const dialogs = odoo.loader.modules.get("@web/core/errors/error_dialogs");
                const titles = {
                    ErrorDialog: String(dialogs.ErrorDialog.title),
                    ClientErrorDialog: String(dialogs.ClientErrorDialog.title),
                    NetworkErrorDialog: String(dialogs.NetworkErrorDialog.title),
                };
                for (const [name, title] of Object.entries(titles)) {
                    if (title.includes("Odoo")) {
                        throw new Error(name + " title still names Odoo: " + title);
                    }
                }
                console.log("test successful");
            })().catch((error) => console.error(error.message));
        """
        self.browser_js(self._display_url(), code, timeout=120)

    def test_customer_display_follows_the_language_of_the_visitor(self):
        # base declares a stub `website` model, so the installed module is looked up instead
        if self.env["ir.module.module"].search_count([("name", "=", "website"), ("state", "=", "installed")]):
            self.skipTest("website restricts the languages a public visitor can pick: it decides this surface")
        self.env["res.lang"]._activate_lang("vi_VN")
        response = self.url_open(self._display_url(), cookies={"frontend_lang": "vi_VN"})
        self.assertRegex(response.text, r"user_context\W+lang\W+vi_VN")


@tagged("post_install", "-at_install")
class TestBackendTemplatesDebrand(HttpCase):

    def test_printer_checklist_of_the_pos_configuration_form_does_not_name_odoo(self):
        code = """
            (async () => {
                for (let i = 0; i < 150; i++) {
                    const templates = odoo.loader.modules.get("@web/core/templates");
                    if (templates) {
                        try {
                            const template = templates.getTemplate("point_of_sale.PosConfigLnaChecklist");
                            if (template) {
                                if (template.textContent.includes("Odoo")) {
                                    throw new Error("the printer checklist still names Odoo");
                                }
                                if (!template.textContent.includes("I use an Epson printer")) {
                                    throw new Error("the Epson checklist item is missing");
                                }
                                console.log("test successful");
                                return;
                            }
                        } catch (error) {
                            if (error.message.includes("printer checklist") || error.message.includes("Epson")) {
                                throw error;
                            }
                        }
                    }
                    await new Promise((resolve) => setTimeout(resolve, 100));
                }
                throw new Error("the printer checklist template never became available");
            })().catch((error) => console.error(error.message));
        """
        self.browser_js("/odoo", code, login="admin", timeout=120)
