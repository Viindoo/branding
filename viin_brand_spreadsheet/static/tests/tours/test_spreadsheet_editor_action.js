/** @odoo-module **/
// Part of Viindoo. See LICENSE file for full copyright and licensing details.
//
// Test-only client action (web.assets_tests), reachable by its registry tag, that mounts a bare CE
// `SpreadsheetComponent` so an HttpCase has a rendered editor to open.
// `SpreadsheetComponent` and `Model` live in the lazy `spreadsheet.o_spreadsheet` bundle, so an
// outer component imports only eager modules and builds the inner component after `loadBundle`
// resolves; a static import would keep this module from ever running.
import { registry } from "@web/core/registry";
import { loadBundle } from "@web/core/assets";
import { Component, onWillStart, useState, xml } from "@odoo/owl";

export const VIIN_TEST_SPREADSHEET_EDITOR_ACTION_TAG =
    "viin_brand_spreadsheet_chrome_dark_test_editor";

class ViinBrandSpreadsheetChromeDarkTestEditor extends Component {
    static template = xml`
        <div class="h-100 w-100">
            <t t-if="state.Inner" t-component="state.Inner"/>
        </div>
    `;
    static props = ["*"];

    setup() {
        this.state = useState({ Inner: null });
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
            class ViinBrandSpreadsheetChromeDarkTestInner extends Component {
                static template = xml`<SpreadsheetComponent model="model"/>`;
                static components = { SpreadsheetComponent };
                static props = ["*"];

                setup() {
                    // Idempotent per env: returns the container the child
                    // `<SpreadsheetComponent>` reuses, so `getStore` below is the engine's own accessor.
                    stores.useStoreProvider();
                    this.model = new Model();
                    window.__viinBrandSpreadsheetChromeDarkTest = {
                        model: this.model,
                        stores,
                        getStore: (Store) => this.env.getStore(Store),
                    };
                }
            }
            this.state.Inner = ViinBrandSpreadsheetChromeDarkTestInner;
        });
    }
}

registry
    .category("actions")
    .add(VIIN_TEST_SPREADSHEET_EDITOR_ACTION_TAG, ViinBrandSpreadsheetChromeDarkTestEditor);
