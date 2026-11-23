# Part of Odoo. See LICENSE file for full copyright and licensing details.
# The editor strings that name the product are checked in a real web client: the core spreadsheet
# unit tests assert the stock wording, so those patches are loaded only outside the unit-test
# bundle. The dialog title patch only touches the spreadsheet dialog and is covered by a Hoot test.
from odoo.modules import Manifest
from odoo.tests.common import HttpCase, TransactionCase, tagged

DIALOG_FILE = "viin_brand_spreadsheet/static/src/dialog/spreadsheet_dialog_title.js"
EDITOR_FILES = (
    "viin_brand_spreadsheet/static/src/chart/chart_menu.js",
    "viin_brand_spreadsheet/static/src/chart/odoo_chart_core_plugin.js",
    "viin_brand_spreadsheet/static/src/data_sources/server_data.js",
    "viin_brand_spreadsheet/static/src/dialog/spreadsheet_dialog_title.js",
    "viin_brand_spreadsheet/static/src/functions/function_category.js",
    "viin_brand_spreadsheet/static/src/o_spreadsheet/link_editor.xml",
)


@tagged("post_install", "-at_install")
class TestSpreadsheetBundles(TransactionCase):

    def _paths(self, bundle):
        return [
            path.lstrip("/")
            for path, _full, _bundle, _mtime in self.env["ir.asset"]._get_asset_paths(
                bundle=bundle, assets_params={}
            )
        ]

    def test_editor_bundle_carries_the_debrand_files_and_the_unit_tests_only_the_dialog_one(self):
        editor = self._paths("spreadsheet.o_spreadsheet")
        unit = self._paths("web.assets_unit_tests")
        for path in EDITOR_FILES:
            with self.subTest(file=path):
                self.assertIn(path, editor)
                if path == DIALOG_FILE:
                    self.assertIn(path, unit)
                else:
                    self.assertNotIn(path, unit)


_PRELUDE = """
const wait = async (predicate) => {
    for (let i = 0; i < 300; i++) {
        const value = predicate();
        if (value) { return value; }
        await new Promise((resolve) => setTimeout(resolve, 100));
    }
    throw new Error("timed out");
};
const { translationIsReady } = await wait(() => odoo.loader.modules.get("@web/core/l10n/translation"));
await translationIsReady;
const { loadBundle } = await wait(() => odoo.loader.modules.get("@web/core/assets"));
await loadBundle("spreadsheet.o_spreadsheet");
"""


def _page_script(body):
    """Wrap ``body`` in the success/failure console contract of ``browser_js``."""
    return "".join((
        "(async () => {\n try {\n",
        _PRELUDE,
        body,
        "\n console.log('test successful');\n } catch (error) {\n",
        " console.error(error.stack || error.message || String(error));\n }\n})();\n",
    ))


@tagged("post_install", "-at_install")
class TestSpreadsheetDependencies(TransactionCase):

    def test_depends_names_viin_brand_whose_tests_the_module_imports(self):
        manifest = Manifest.for_addon("viin_brand_spreadsheet", display_warning=False)
        self.assertIn("viin_brand", manifest["depends"])


@tagged("post_install", "-at_install")
class TestSpreadsheetEditorDebrand(HttpCase):

    def _run(self, body):
        self.browser_js("/odoo", _page_script(body), login="admin", timeout=180)

    def test_function_categories_are_not_named_odoo(self):
        self._run("""
            const { registries } = odoo.loader.modules.get("@odoo/o-spreadsheet");
            const { functionRegistry } = registries;
            const legacy = Object.entries(functionRegistry.content)
                .filter(([, description]) => description.category === "Odoo")
                .map(([name]) => name);
            if (legacy.length) {
                throw new Error("functions still filed under Odoo: " + legacy.join(", "));
            }
            if (functionRegistry.content["ODOO.LIST"].category !== "Viindoo") {
                throw new Error("ODOO.LIST category: " + functionRegistry.content["ODOO.LIST"].category);
            }
            functionRegistry.add("VIIN.TEST.LATE", { description: "x", args: [], compute: () => 1, category: "Odoo" });
            if (functionRegistry.content["VIIN.TEST.LATE"].category !== "Viindoo") {
                throw new Error("a late function stays under Odoo");
            }
        """)

    def test_function_help_does_not_name_odoo(self):
        self._run("""
            const { registries } = odoo.loader.modules.get("@odoo/o-spreadsheet");
            const { functionRegistry } = registries;
            const named = Object.entries(functionRegistry.content)
                .filter(([, description]) => description.category === "Viindoo")
                .filter(([, description]) => String(description.description).includes("Odoo"))
                .map(([name]) => name);
            if (named.length) {
                throw new Error("function help still names Odoo: " + named.join(", "));
            }
            if (!String(functionRegistry.content["ODOO.LIST"].description)) {
                throw new Error("ODOO.LIST lost its description");
            }
        """)

    def test_untitled_chart_is_named_after_its_type_without_odoo(self):
        self._run("""
            const { OdooChartCorePlugin } = odoo.loader.modules.get(
                "@spreadsheet/chart/plugins/odoo_chart_core_plugin"
            );
            const plugin = (title) => Object.assign(Object.create(OdooChartCorePlugin.prototype), {
                charts: { a: {} },
                getters: { getChartDefinition: () => ({ title: { text: title }, type: "line" }) },
            });
            const untitled = plugin("").getOdooChartDisplayName("a");
            if (untitled.includes("Odoo") || !untitled.includes("Viindoo")) {
                throw new Error("untitled chart: " + untitled);
            }
            const titled = plugin("Odoo sales").getOdooChartDisplayName("a");
            if (!titled.includes("Odoo sales")) { throw new Error("a typed title was changed: " + titled); }
        """)

    def test_chart_menu_entry_that_opens_the_linked_record_does_not_name_odoo(self):
        self._run("""
            const { components } = odoo.loader.modules.get("@odoo/o-spreadsheet");
            const menu = Object.create(components.ChartMenu.prototype);
            Object.defineProperty(menu, "hasOdooLink", { value: true });
            Object.defineProperty(menu, "env", { value: { model: { getters: { isDashboard: () => false } } } });
            Object.defineProperty(menu, "props", { value: { chartId: "a" } });
            Object.defineProperty(menu, "fullScreenMenuItem", { value: undefined });
            menu.getAnnotationLink = () => undefined;
            menu.getAnnotationText = () => undefined;
            const item = menu.getMenuItems().find((entry) => entry.id === "chartOdooLink");
            if (!item) { throw new Error("the chart menu has no entry for the linked record"); }
            if (String(item.label).includes("Odoo")) { throw new Error("chart menu entry: " + item.label); }
        """)

    def test_failed_formula_data_message_points_to_the_support_site_of_the_vendor(self):
        self._run("""
            const { BatchEndpoint } = odoo.loader.modules.get("@spreadsheet/data_sources/server_data");
            const results = BatchEndpoint.prototype._handleBatchFailure.call({}, { requests: [{}] });
            const [error] = results.values();
            if (error.message.includes("odoo.com")) { throw new Error("the message reads: " + error.message); }
            if (!error.message.includes("viindoo.com")) { throw new Error("the message reads: " + error.message); }
        """)

    def test_link_url_placeholder_is_a_neutral_example(self):
        self._run("""
            const { getTemplate } = odoo.loader.modules.get("@web/core/templates");
            const template = getTemplate("o-spreadsheet-LinkEditor");
            const input = template.querySelector('[t-ref="this.urlInput"]');
            if (!input || !input.getAttribute("placeholder")) {
                throw new Error("the link input lost its placeholder");
            }
            const text = [...template.querySelectorAll("*")]
                .map((el) => el.getAttribute("placeholder") || "").join(" ");
            if (/odoo[.]com/i.test(text)) { throw new Error("link placeholder names odoo.com"); }
        """)
