# Part of Odoo. See LICENSE file for full copyright and licensing details.
# The editor strings that name the product are checked in a real web client: the core spreadsheet
# unit tests assert the stock wording, so those patches are loaded only outside the unit-test
# bundle. The dialog title patch only touches the spreadsheet dialog and is covered by a Hoot test.
from odoo.modules import Manifest
from odoo.tests.common import HttpCase, TransactionCase, tagged

DIALOG_FILE = "viin_brand_spreadsheet/static/src/dialog/confirmation_dialog.js"
EDITOR_FILES = (
    "viin_brand_spreadsheet/static/src/chart/odoo_chart_core_plugin.js",
    "viin_brand_spreadsheet/static/src/dialog/confirmation_dialog.js",
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

    def test_untitled_chart_is_named_after_its_type_without_odoo(self):
        self._run("""
            const { OdooChartCorePlugin } = odoo.loader.modules.get("@spreadsheet/chart/plugins/odoo_chart_core_plugin");
            const plugin = (title) => ({
                getters: { getChart: () => ({ title: { text: title }, type: "odoo_line" }) },
                getOdooChartIds: () => ["a"],
            });
            const untitled = OdooChartCorePlugin.prototype.getOdooChartDisplayName.call(plugin(""), "a");
            if (untitled !== "(#1) Viindoo Line Chart") { throw new Error("untitled chart: " + untitled); }
            const titled = OdooChartCorePlugin.prototype.getOdooChartDisplayName.call(plugin("Odoo sales"), "a");
            if (titled !== "(#1) Odoo sales") { throw new Error("a typed title was changed: " + titled); }
        """)

    def test_link_url_placeholder_is_a_neutral_example(self):
        self._run("""
            const { getTemplate } = odoo.loader.modules.get("@web/core/templates");
            const template = getTemplate("o-spreadsheet-LinkEditor");
            const text = template.textContent + [...template.querySelectorAll("*")]
                .map((el) => el.getAttribute("placeholder") || "").join(" ");
            if (!text.includes("e.g. 'https://www.example.com'")) { throw new Error("link placeholder reads: " + text); }
            if (text.includes("odoo.com")) { throw new Error("link placeholder names odoo.com"); }
        """)
