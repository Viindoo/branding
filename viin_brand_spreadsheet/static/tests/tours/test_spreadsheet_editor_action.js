// Part of Viindoo. See LICENSE file for full copyright and licensing details.
//
// Test-only client action (web.assets_tests), reachable by its registry tag, that mounts a bare CE
// `SpreadsheetComponent` so an HttpCase has a rendered editor to open.
// `SpreadsheetComponent` and `Model` live in the lazy `spreadsheet.o_spreadsheet` bundle, so an
// outer component imports only eager modules and builds the inner component after `loadBundle`
// resolves; a static import would keep this module from ever running.
import { Component, onWillStart, useProps, xml } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { cookie } from "@web/core/browser/cookie";
import { registry } from "@web/core/registry";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";

export const VIIN_TEST_SPREADSHEET_EDITOR_ACTION_TAG = "viin_brand_spreadsheet_palette_test_editor";

class ViinBrandSpreadsheetPaletteTestEditor extends Component {
    static template = xml`
        <div class="h-100 w-100">
            <t t-component="this.Inner"/>
        </div>
    `;
    props = useProps({ ...standardActionServiceProps });

    setup() {
        onWillStart(async () => {
            await loadBundle("spreadsheet.o_spreadsheet");
            const engine = odoo.loader.modules.get("@odoo/o-spreadsheet");
            const spreadsheetComponentModule = odoo.loader.modules.get(
                "@spreadsheet/actions/spreadsheet_component"
            );
            if (!engine || !spreadsheetComponentModule) {
                // Fail loudly instead of leaving an editor that never mounts.
                throw new Error(
                    "viin_brand_spreadsheet test editor: loadBundle('spreadsheet.o_spreadsheet') " +
                        "did not register the expected core modules " +
                        "(@odoo/o-spreadsheet, @spreadsheet/actions/spreadsheet_component)."
                );
            }
            const { Model, stores } = engine;
            const { SpreadsheetComponent } = spreadsheetComponentModule;

            // Built after `loadBundle` so `SpreadsheetComponent` is defined when referenced.
            class ViinBrandSpreadsheetPaletteTestInner extends Component {
                static template = xml`<SpreadsheetComponent model="this.model"/>`;
                static components = { SpreadsheetComponent };

                setup() {
                    // Idempotent per env: returns the container the child
                    // `<SpreadsheetComponent>` reuses.
                    stores.useStoreProvider();
                    // The engine paints in the scheme its model is configured with, as the dashboards do.
                    this.model = new Model({}, { colorScheme: cookie.get("color_scheme") });
                }
            }
            this.Inner = ViinBrandSpreadsheetPaletteTestInner;
        });
    }
}

registry
    .category("actions")
    .add(VIIN_TEST_SPREADSHEET_EDITOR_ACTION_TAG, ViinBrandSpreadsheetPaletteTestEditor);
