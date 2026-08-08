/** @odoo-module **/

import { expect, getFixture, test } from "@odoo/hoot";

// Cross-module reach into point_of_sale's OWN test helpers, from a different module - the exact
// idiom pos_hr, pos_discount, pos_stripe and pos_online_payment_self_order already use to reach
// "point_of_sale/static/tests/unit/..." (e.g. pos_discount/static/tests/unit/data/
// product_template.data.js: `import { PosConfig } from "@point_of_sale/../tests/unit/data/
// pos_config.data"`), mirroring this repo's own "@web/../tests/web_test_helpers" idiom.
import { setupPosEnv } from "@point_of_sale/../tests/unit/utils";
import { definePosModels } from "@point_of_sale/../tests/unit/data/generate_model_definitions";
import { mountWithCleanup } from "@web/../tests/web_test_helpers";

// Real point_of_sale Navbar - no mock. See header comment below for why a module-shadow mock is
// structurally impossible in this checkout and was removed (mock_navbar_module.js deleted).
import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
import "@viin_brand_pos/app/navbar/navbar";

definePosModels();

// viin_brand_pos/static/src/app/navbar/navbar.js patches Navbar.prototype.setup() to set a
// branded favicon from the current POS company:
//     const favicon = `/web/image/res.company/${this.pos.company.id}/favicon`;
// Business rule under protection: setup() must overwrite the href of every non-apple-touch-icon
// <link rel*="icon"> element in the document with that branded favicon URL, once a current POS
// company is available.
//
// RE-GROUNDED this session (adapt-mode repair of a RED-for-the-wrong-reason test; static reading
// of a real v19.0 core checkout at /home/tran-ngoc-tuan/git/odoo_19.0, no instance provisioned):
//
// Why the prior module-shadow mock (mock_navbar_module.js, now deleted) could never work here:
// 1. addons/point_of_sale/__manifest__.py's `web.assets_unit_tests_setup` bundle - the shared Hoot
//    bootstrap EVERY unit test file loads against - includes `point_of_sale.assets_prod`, which
//    includes `point_of_sale._assets_pos`, which globs `point_of_sale/static/src/**/*` with only
//    backend/**, customer_display/** (partially) and main.js excluded. The REAL
//    app/components/navbar/navbar.js is NOT excluded, so it loads as part of that setup bundle -
//    BEFORE `web.assets_unit_tests` (which carried the mock) ever runs.
// 2. `web/static/src/module_loader.js`'s `ModuleLoader.define()` ignores a duplicate module name
//    ("first registration wins"). Since the real Navbar registers first (point 1), the mock's own
//    later `odoo.define()` for the same name was silently ignored - `import { Navbar } from
//    "@point_of_sale/app/components/navbar/navbar"` always resolved to the REAL class, never the
//    mock, regardless of what mock_navbar_module.js declared.
// 3. Even if the shadow had won, `Object.create(Navbar.prototype)` + a bare `navbar.setup()` call
//    can never satisfy an OWL hook: `usePos()` (the real Navbar.setup()'s first statement, and -
//    because `@web/core/utils/patch.js` bakes the pre-patch method into a skeleton captured from
//    the REAL class - also what this module's patched `super.setup()` always calls) reads OWL's
//    global "current render node", which OWL's own component-construction machinery populates only
//    while an actual `Component` is being mounted by the framework. A bare method call outside that
//    construction path leaves the node `null`, which is the exact source of the observed failure
//    ("Cannot read properties of null (reading 'component')", from `useComponent()` in
//    `web/static/lib/owl/owl.js`).
//
// The fix: mount the REAL Navbar through OWL, the same way core itself does. This is not a novel
// pattern - it is lifted directly from PASSING precedent in this exact checkout:
// - addons/point_of_sale/static/tests/unit/components/orderline_note_button.test.js and siblings
//   under the same directory show the canonical shape for any component whose setup() touches
//   usePos()/POS services: `definePosModels()` once at module top level, then per test
//   `const store = await setupPosEnv(); ... await mountWithCleanup(SomeComponent, {...});`.
// - addons/pos_hr/static/tests/unit/components/navbar/navbar.test.js is the strongest precedent:
//   ANOTHER module (like this one) that patches/reads off the real Navbar, mounting the exact same
//   component the exact same way (`await mountWithCleanup(Navbar, {})` after `setupPosEnv()`), and
//   it passes. No module-shadow mock, no Object.create() - just a real mount.
// `setupPosEnv()` (addons/point_of_sale/static/tests/unit/utils.js) stands up a genuine POS store
// + OWL env, so `usePos()` resolves for real - no hook-satisfying trickery needed.
//
// addons/point_of_sale/static/src/app/services/pos_store.js:407-409 defines
// `get company() { return this.config.company_id; }` - a plain, always-available getter (also
// listed in `static excludedLazyGetters`, same file), so `this.pos.company` can never be undefined
// once `usePos()` has run: the invariant is structural, not a runtime maybe-missing condition. The
// assertion below reads the expected company id off the SAME live store instance the patched
// setup() itself reads (`store` returned by `setupPosEnv()` IS the singleton `usePos()` resolves
// to), never a hardcoded literal and never a recomputation of the production formula.
//
// No `describe.tags(...)`: every POS component-mount test cited above (all seven files under
// point_of_sale/static/tests/unit/components/, and pos_hr's own navbar.test.js) carries none - a
// real OWL mount through `setupPosEnv()`/`mountWithCleanup()` is not a "headless" suite, so the
// prior `describe.current.tags("headless")` (inherited from the Object.create()-based test that
// never actually mounted anything) is dropped rather than carried forward on a stale assumption.
//
// Dropped: the 18.0-era "bails out early without throwing when there is no current company" test.
// It asserted a defensive guard (`const currentCompany = this.env.services.company?.currentCompany;
// if (!currentCompany) { return; }`) that the current, resolved production code does not have -
// the code now reads `this.pos.company.id` unconditionally, with no guard. That guarded branch is
// not just absent from the code, it is structurally unreachable in real production: by the time
// the patched setup() runs `this.pos.company.id`, `super.setup()` has already run `usePos()`, and
// `this.pos.company` is a plain, always-available getter - there is no code path where `this.pos`
// is set but `company` is missing. Per the adapt-mode contract, a test asserting an unreachable
// branch is dropped rather than kept red-for-the-wrong-reason or given a fabricated new negative
// case - no replacement negative-path assertion is introduced here.
test("branded POS navbar setup() sets the favicon from the current company when one is available", async () => {
    const icon = document.createElement("link");
    icon.rel = "icon";
    icon.href = "/original-favicon.ico";
    getFixture().appendChild(icon);

    const store = await setupPosEnv();
    await mountWithCleanup(Navbar, {});

    expect(icon.getAttribute("href")).toBe(`/web/image/res.company/${store.company.id}/favicon`);
});
