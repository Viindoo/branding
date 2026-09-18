/** @odoo-module **/
// Part of Viindoo. See LICENSE file for full copyright and licensing details.
//
// TEST-ONLY infrastructure (web.assets_tests, never web.assets_backend). CE's spreadsheet addon
// registers no editor client action of its own outside a business module's data - only a
// download action, a lazy-bundle loader and the dashboard action - so there is no core route into
// a rendered CE editor for an HttpCase to open. This file is that route: a client action reachable
// by its bare registry TAG (env.services.action.doAction(<tag>) resolves a registered string with
// zero server round-trip - web/static/src/webclient/actions/action_service.js _loadAction), which
// loads the lazy `spreadsheet.o_spreadsheet` bundle and mounts the CE `SpreadsheetComponent` on a
// bare `new Model()` - CORE classes only, never a business-module selector or template, so this
// fixture keeps mounting a bare CE editor even on a checkout with no business module installed.
//
// WHY TWO COMPONENT CLASSES, NOT ONE. `SpreadsheetComponent`/`Model` live inside the LAZY
// `spreadsheet.o_spreadsheet` bundle, undefined until `loadBundle()` resolves. A static top-level
// `import` of either name here would leave THIS file's own module queued behind that undefined
// dependency (odoo/web's ModuleLoader only starts a module once every one of its deps is already
// in `this.modules` - web/static/src/module_loader.js `findJob`/`startModule`), so the very
// `registry.category("actions").add(...)` call that makes this action reachable would never run -
// nothing would ever be left to call `loadBundle` in the first place. CE's own lazy actions solve
// this by splitting the always-eager stub from the bundle-only real component
// (spreadsheet/static/src/assets_backend/spreadsheet_action_loader.js); this file solves it the
// same way, but as ONE outer component that only ever imports always-eager `@web/...`/`@odoo/owl`
// modules, plus an INNER component class built dynamically - after `loadBundle` resolves - from
// the two spreadsheet modules read out of `odoo.loader.modules` (the loader's own public
// name -> resolved-exports map, populated once a module has actually run).
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
                // A broken measurement, never a silent no-op: surfaces as a console error the
                // HttpCase's own browser_js wait already treats as a hard failure, rather than an
                // editor that quietly never mounts.
                throw new Error(
                    "viin_brand_spreadsheet test editor: loadBundle('spreadsheet.o_spreadsheet') " +
                        "did not register the expected core modules " +
                        "(@odoo/o-spreadsheet, @spreadsheet/actions/spreadsheet_component)."
                );
            }
            const { Model, stores } = engine;
            const { SpreadsheetComponent } = spreadsheetComponentModule;

            // Built here (not at module scope) precisely so its own `SpreadsheetComponent`
            // sub-component reference only ever resolves AFTER the bundle that defines it has
            // already loaded - see the module docstring above.
            class ViinBrandSpreadsheetChromeDarkTestInner extends Component {
                static template = xml`<SpreadsheetComponent model="model"/>`;
                static components = { SpreadsheetComponent };
                static props = ["*"];

                setup() {
                    // `stores.useStoreProvider()` is idempotent per env
                    // (o_spreadsheet.js store_hooks.ts): it returns the SAME
                    // DependencyContainer this component's own `<SpreadsheetComponent>` /
                    // `<Spreadsheet>` descendant will find (and reuse, never replace) via its own
                    // identical call once mounted - because ours runs first and stamps
                    // `env.__spreadsheet_stores__` before the child tree renders. Exposing
                    // `this.env.getStore` here is therefore the SAME accessor the engine's own
                    // side-panel / cell-popover UI uses internally, not a second, parallel one.
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
