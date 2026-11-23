from odoo import Command
from odoo.tests import Form, HttpCase, tagged


@tagged('post_install', '-at_install')
class TestSubcontractingPortalClient(HttpCase):
    """The standalone web client of the subcontracting portal names no Odoo on the surfaces a
    subcontractor meets: the tab title, the default dialog title, the error dialogs and the
    session-expired notice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = cls.env['res.users'].with_context(no_reset_password=True, mail_create_nolog=True).create({
            'name': 'Subcontractor',
            'login': 'brand_subcontractor',
            'password': 'brand_subcontractor',
            'email': 'brand_subcontractor@example.com',
            'group_ids': [Command.set([cls.env.ref('base.group_portal').id])],
        })
        partner = user.partner_id
        component = cls.env['product.product'].create({'name': 'Component', 'is_storable': True})
        finished = cls.env['product.product'].create({'name': 'Finished', 'is_storable': True})
        bom_form = Form(cls.env['mrp.bom'])
        bom_form.type = 'subcontract'
        bom_form.subcontractor_ids.add(partner)
        bom_form.product_tmpl_id = finished.product_tmpl_id
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = component
            bom_line.product_qty = 1
        bom_form.save()
        picking_form = Form(cls.env['stock.picking'])
        picking_form.picking_type_id = cls.env.ref('stock.picking_type_in')
        picking_form.partner_id = partner
        with picking_form.move_ids.new() as move:
            move.product_id = finished
            move.product_uom_qty = 2
        cls.picking = picking_form.save()
        cls.picking.action_confirm()

    def test_portal_client_names_no_odoo_in_its_title_dialogs_and_errors(self):
        code = """
            (async () => {
                const wait = async (condition, label) => {
                    for (let i = 0; i < 150; i++) {
                        const value = condition();
                        if (value) {
                            return value;
                        }
                        await new Promise((resolve) => setTimeout(resolve, 100));
                    }
                    throw new Error("timeout waiting for: " + label);
                };
                const env = await wait(() => odoo.__WOWL_DEBUG__?.root?.env, "the client is mounted");
                await wait(() => document.querySelector(".o_form_view"), "the form view is rendered");
                const module = (name) => odoo.loader.modules.get(name);
                const dialogTitle = async (Dialog, props) => {
                    const close = env.services.dialog.add(Dialog, props);
                    const title = await wait(() => document.querySelector(".o_dialog .modal-title"), "a dialog title");
                    const text = title.textContent;
                    close();
                    await wait(() => !document.querySelector(".o_dialog"), "the dialog is closed");
                    return text;
                };
                const seen = {
                    "tab title": document.title,
                    "error dialog": await dialogTitle(module("@web/core/errors/error_dialogs").ErrorDialog, {
                        traceback: "boom",
                    }),
                    "default dialog": await dialogTitle(
                        module("@web/webclient/actions/action_dialog").ActionDialog, {}
                    ),
                };
                const sessionExpired = module("@web/core/registry").registry
                    .category("error_notifications")
                    .get("odoo.http.session.SessionExpiredException");
                seen["session expired"] = String(sessionExpired.message);
                for (const [surface, text] of Object.entries(seen)) {
                    if (/odoo/i.test(text)) {
                        throw new Error(surface + " names Odoo: " + text);
                    }
                }
                if (!/viindoo/i.test(seen["default dialog"])) {
                    throw new Error("the default dialog title is not Viindoo: " + seen["default dialog"]);
                }
                console.log("test successful");
            })().catch((error) => console.error(error.message));
        """
        url = '/my/productions/%s/subcontracting_portal' % self.picking.id
        self.browser_js(url, code, login='brand_subcontractor', timeout=180)
