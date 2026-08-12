import { describe, expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { click, queryText } from "@odoo/hoot-dom";
import {
    makeDialogMockEnv,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";

// Core web.UpgradeDialog (the Enterprise-upsell dialog opened from any `upgrade_boolean` field,
// e.g. Settings > General Settings > any CE-gated toggle):
// odoo/addons/web/static/src/webclient/settings_form_view/fields/upgrade_dialog.js
import { UpgradeDialog } from "@web/webclient/settings_form_view/fields/upgrade_dialog";

describe.current.tags("desktop");

// Business rules under protection (PR #633 rebase verdict c2-common.md finding R-7 + owner
// decision D3, MASTER_DESIGN_DOC plan.md decisions table):
//
// (1) The dialog's primary CTA ("Upgrade now", UpgradeDialog._confirmUpgrade()) must NEVER send
//     the customer to odoo.com - it must open a Viindoo URL instead. Core hardcodes
//     `window.open("https://www.odoo.com/odoo-enterprise/upgrade?num_users=" + usersCount)`
//     (upgrade_dialog.js, verbatim above) and viin_brand_web has never patched it - R-7's exact
//     finding: "the dialog *looks* de-branded [only the template was patched] ... the primary CTA
//     still sends the customer to odoo.com".
// (2) The dialog's title and promotional body copy must never carry the "Odoo" or "Viindoo"
//     wordmark - per owner decision D3 the de-brand wordmark is "System" everywhere, superseding
//     the module's earlier "Viindoo" convention (the same D3 that already flipped
//     viin_brand_web/static/src/core/dialog/dialog.js and
//     viin_brand_web/static/src/core/errors/error_dialogs.js from "Viindoo" to "System").
//
// DELIBERATELY NO side-effect import of a viin_brand_web production module here, unlike this
// module's other `*_debrand` tests (documentation_link_debrand.test.js, user_menu_debrand.test.js,
// colors_debrand.test.js import their patch module as a side effect so a prototype/export mutation
// runs before the test body). That idiom exists to force a patch to run when the test would
// otherwise never touch the module that applies it. Here it is unnecessary and would only pin a
// path this WI has not yet created (the fix is expected to land as a NEW JS patch file plus a
// RELOCATED XML template, per this WI's brief - the exact filename is a coder decision, not a test
// concern per ODOO-AI-ETHOS #4 outcomes-over-procedures):
//   - the CTA fix will be a `patch(UpgradeDialog.prototype, { async _confirmUpgrade() {...} })`.
//     `patch()` mutates the SAME class object this file imports directly from core - once that
//     patch module is wired into `web.assets_backend` (an EAGER, bare-string bundle entry per this
//     WI's plan), Hoot's `ModuleSetLoader.setup()` runs it before any test file's own module runs
//     (web/static/src/module_loader.js:218-236, see user_menu_debrand.test.js's header comment
//     for the full mechanism), so mounting the imported `UpgradeDialog` below already observes
//     the patched method - no re-import required.
//   - the wordmark fix is a QWeb `t-inherit="web.UpgradeDialog"` template, not a JS module; XML
//     template extensions are registered globally by `t-name` when their owning bundle loads,
//     never imported by JS specifier. Once wired into `web.assets_backend`, mounting
//     `UpgradeDialog` picks up the override automatically, like every other backend view here.
//
// RED-before-green, confirmed by READING today's on-disk source (no live instance this session):
//   - CTA: core's `_confirmUpgrade()` is untouched and no viin_brand_web file patches it, so
//     clicking "Upgrade now" today calls `window.open("https://www.odoo.com/odoo-enterprise/...")`
//     - test 1's `not.toMatch(/odoo\.com/i)` fails today for exactly that reason.
//   - Wordmark: `viin_brand_web/static/src/webclient/settings_form_view/fields/
//     upgrade_dialog.xml` exists on disk but is NOT referenced by any manifest bundle key today
//     (manifest comment: "NOT WIRED, deliberately ... it is inert"), so mounting `UpgradeDialog`
//     today renders core's OWN unmodified template - title "Odoo Enterprise", body "Get this
//     feature and much more with Odoo Enterprise!" - both containing the literal "Odoo" wordmark.
//     Test 2's `not.toMatch(/Odoo/i)` on `.modal-title` and on the body text both fail today for
//     that reason (even the module's own stale override, were it wired, would still fail: it says
//     "Viindoo Enterprise", pre-dating D3 and failing the `toMatch(/System/)` /
//     `not.toMatch(/Viindoo/i)` assertions instead).

test("clicking Upgrade now never opens odoo.com - it opens Viindoo's own page", async () => {
    // usersCount is read via orm.call("res.users", "search_count", ...) before window.open() is
    // called; mock it so _confirmUpgrade() can run to completion regardless of which model backs
    // it, matching this suite's onRpc(method, handler) idiom (e.g. settings_form_view.test.js).
    onRpc("search_count", () => 7);

    const openedUrls = [];
    patchWithCleanup(window, {
        open: (url) => {
            openedUrls.push(String(url));
        },
    });

    const env = await makeDialogMockEnv();
    await mountWithCleanup(UpgradeDialog, { env, props: { close: () => {} } });

    await click(".modal-footer .btn-primary");
    await animationFrame();

    // Guard against a vacuous pass: the CTA must actually have tried to open something.
    expect(openedUrls).toHaveLength(1);
    expect(openedUrls[0]).not.toMatch(/odoo\.com/i);
    expect(openedUrls[0]).toMatch(/^https:\/\/viindoo\.com\//);
});

test("the Enterprise-upgrade dialog copy never carries Odoo/Viindoo - only System", async () => {
    const env = await makeDialogMockEnv();
    await mountWithCleanup(UpgradeDialog, { env, props: { close: () => {} } });

    const titleText = queryText("header .modal-title");
    expect(titleText).not.toMatch(/Odoo/i);
    expect(titleText).not.toMatch(/Viindoo/i);
    expect(titleText).toMatch(/System/);

    // queryText() reads rendered TEXT content only (not markup/attributes), so the retained
    // "https://viindoo.com/pricing?..." href on the "And more" link - a domain reference, not the
    // brand wordmark - cannot false-positive this assertion; only visible wordmark text can.
    const bodyText = queryText(".modal-body");
    expect(bodyText).not.toMatch(/Odoo/i);
    expect(bodyText).not.toMatch(/Viindoo/i);
    expect(bodyText).toMatch(/System/);
});
