import { beforeEach, describe, expect, test } from "@odoo/hoot";

// Core registers its stock user-menu entries as a plain module side effect
// (web/static/src/webclient/user_menu/user_menu_items.js:137-145):
//   "support" -> supportItem, "shortcuts", "separator", "preferences",
//   "odoo_account" -> odooAccountItem, "install_pwa", "log_out".
// viin_brand_common deletes two of those keys and substitutes Viindoo entries
// (static/src/webclient/user_menu_item.js:50-57). `Registry.remove()` is
// `delete this.content[key]` with NO existence check and NO throw
// (web/static/src/core/registry.js:176-181), so a core RENAME of either key turns both calls into
// silent no-ops. Import the REAL, unmodified patch as a side effect so its registry mutation runs
// before any test body executes (same idiom as documentation_link_debrand.test.js).
import { registry } from "@web/core/registry";
import { allowTranslations, serverState } from "@web/../tests/web_test_helpers";
import { odooAccountItem } from "@web/webclient/user_menu/user_menu_items";
import "@viin_brand_common/webclient/user_menu_item";

describe.current.tags("headless");

// Every assertion below reads an item's `description`, which core and this module alike build with
// `_t(...)`. A headless suite loads no localization service, so `translatedTerms[translationLoaded]`
// is still false and every `_t()` returns a LAZY `TranslatedString` whose `valueOf()` THROWS
// "Cannot translate string: translations have not been loaded"
// (web/static/src/core/l10n/translation.js:154, :168). Core's shortcuts entry forces that `valueOf`
// eagerly, inside the factory, by interpolating `_t("Shortcuts")` into a `markup` template
// (web/static/src/webclient/user_menu/user_menu_items.js:39-43), so merely BUILDING the menu throws
// and every test below would die before asserting anything - a suite that proves nothing while
// looking busy. `allowTranslations()` is core's own remedy for exactly this situation: same
// `beforeEach(() => { allowTranslations(); ... })` shape as
// web/static/tests/views/fields/formatters.test.js:28-29, and see
// point_of_sale/static/tests/unit/services/render_service.test.js:19 - "this is needed because we
// are not loading the localization service".
//
// `allowTranslations()` and NOT `patchTranslations({...})`: it flips the loaded flag and registers
// its own `after()` restore (web/static/tests/_framework/translation_test_helpers.js:22-27) WITHOUT
// injecting any term, so `translatedTerms` stays empty and every `_t(source)` resolves to `source`
// - the exact English text that ships. Injecting terms would let a fake translation of
// "My Odoo.com Account" launder the very branding string the sweep below exists to catch; this
// keeps the guards reading the real strings.
beforeEach(() => {
    allowTranslations();
});

// WHAT BREAKS IN PRODUCTION IF ANY TEST BELOW GOES RED
// ----------------------------------------------------
// Odoo's own "My Odoo.com Account" entry (and its "Help" entry pointing at odoo.com support)
// ships in the user menu of a Viindoo-branded build, sitting right next to our
// "My Viindoo.com account" / "Support" replacements - two competing account links in the same
// dropdown, one of them Odoo-branded. Because `Registry.remove()` never throws on a missing key,
// this failure is SILENT: the whole suite stays green while the branded entry reappears in the UI.
//
// WHY THESE ASSERTIONS AND NOT "the key is absent"
// ------------------------------------------------
// A key-absence check (`get("odoo_account", null) === null`) passes VACUOUSLY the moment core
// renames the key - which is the exact drift we are guarding against. So the guards below assert
// on what the user actually sees (the built menu descriptors) and on core's own exported factory
// IDENTITY, neither of which a key rename can defeat.
//
// A temporal "before the patch" snapshot is NOT observable in Hoot, and no fake one is used here:
// `ModuleSetLoader.setup()` executes every module of the suite's addon closure before the test
// file's own module runs (web/static/tests/_framework/module_set.hoot.js), and `startModule()`
// resolves a factory's dependencies BEFORE calling it (web/static/src/module_loader.js:218-236),
// so by the time any statement in this file executes, the patch has already been applied. The
// precondition is therefore asserted against core's registration directly - see
// "core's own Odoo.com account factory" below.

/** Minimal env carrying only what core's item factories read EAGERLY while BUILDING a descriptor:
 * `env.isSmall` (shortcuts, user_menu_items.js:38), `env.services.menu.getCurrentApp()`
 * (install_pwa, :94) and `env.services.pwa.isScopedApp` (log_out, :121). Every other env access in
 * core's factories lives inside a `callback`/`show` closure that is never invoked here. */
function makeEnv() {
    return {
        isSmall: false,
        services: {
            menu: { getCurrentApp: () => null },
            pwa: { isScopedApp: false },
        },
    };
}

/** Build every descriptor the user menu would render, exactly the way core's UserMenu does at
 * render time: `userMenuRegistry.getAll().map((element) => element(this.env))`
 * (web/static/src/webclient/user_menu/user_menu.js:26-28). */
function getUserMenuItems() {
    const env = makeEnv();
    return registry
        .category("user_menuitems")
        .getAll()
        .map((itemFactory) => itemFactory(env));
}

/** The single entry the menu offers for a given item id, asserting there is exactly one. */
function uniqueItemById(items, id) {
    const matches = items.filter((item) => item.id === id);
    expect(matches).toHaveLength(1);
    return matches[0];
}

test("no user menu entry may carry Odoo branding", () => {
    const items = getUserMenuItems();
    // Guard against a vacuous pass: an empty menu would satisfy the loop below trivially.
    expect(items.length).toBeGreaterThan(0);
    for (const item of items) {
        // `description` is a plain string for most entries but a Markup object for core's
        // shortcuts entry (user_menu_items.js:39), and the separator has none at all - so coerce
        // before matching rather than assume a string.
        expect(String(item.description ?? "")).not.toMatch(/odoo\.com/i);
        expect(String(item.href ?? "")).not.toMatch(/odoo\.com/i);
    }
});

test("core's own Odoo.com account factory must not survive under any registry key", () => {
    // PRECONDITION, asserted against core's registration directly: core still exports the
    // Odoo-branded account factory it registers under "odoo_account"
    // (user_menu_items.js:72 `export function odooAccountItem`, registered at :143). Odoo's
    // transpiler turns this file's named import into a destructuring `require`, so a core rename
    // of the EXPORT would silently bind `undefined` here and make the outcome assertion vacuous -
    // this line makes that case fail LOUD instead. A rename of the MODULE PATH fails even louder,
    // at load time.
    expect(odooAccountItem).toBeInstanceOf(Function);

    // OUTCOME, rename-proof: the exact factory object core registers is no longer reachable under
    // ANY key. If core renames "odoo_account", `remove("odoo_account")` no-ops and this factory is
    // still in the registry under the new key - caught here.
    expect(registry.category("user_menuitems").getAll()).not.toInclude(odooAccountItem);

    // Weaker companion, kept only because it pins the key this module actually deletes today: it
    // passes vacuously after a core rename, which is precisely why it is NOT the load-bearing
    // assertion of this test.
    expect(registry.category("user_menuitems").get("odoo_account", null)).toBe(null);
});

test("the user menu must never offer two entries for the same action", () => {
    // Core's supportItem and ours both build `id: "support"` (user_menu_items.js:14 vs
    // user_menu_item.js:26); core's odooAccountItem and ours both build `id: "account"` (:75 vs
    // :39). So a silently no-op `remove()` shows up here as a duplicate id - the exact production
    // symptom of an Odoo-branded entry shipping beside its Viindoo replacement. This catches a
    // rename of core's registry KEY without depending on any key name. That id alignment is
    // LOAD-BEARING for this guard: renaming our items' ids to e.g. "viindoo_support" would make a
    // resurrected stock entry stop colliding, and core's stock support entry carries no odoo.com
    // href to be caught by the branding sweep above (its url is `session.support_url`,
    // user_menu_items.js:11, which the mocked Hoot session does not define).
    const ids = getUserMenuItems()
        .map((item) => item.id)
        .filter(Boolean);
    const duplicated = ids.filter((id, index) => ids.indexOf(id) !== index);
    expect(duplicated).toEqual([]);
});

test("the user menu's documentation, support and account entries must point at Viindoo", () => {
    const items = getUserMenuItems();
    // Core's stock entries carry no href at all (odooAccountItem opens its URL from an RPC
    // callback) or an odoo.com one, so asserting the surviving entry's href is asserting that the
    // Viindoo replacement - not the stock entry - is the one the user clicks.
    expect(uniqueItemById(items, "documentation").href).toMatch(/^https:\/\/viindoo\.com\//);
    expect(uniqueItemById(items, "support").href).toMatch(/^https:\/\/viindoo\.com\//);
    expect(uniqueItemById(items, "account").href).toMatch(/^https:\/\/viindoo\.com\//);
});

test("the documentation link must follow the running server's series, never a pinned literal", () => {
    // Same silent-drift class as the `remove()` no-op above: a documentation URL that PINS its
    // series literal keeps rendering happily after a forward-port to a new series - nothing
    // raises, the user just lands on the wrong (or missing) documentation tree. The de-branded
    // link must track the server the user is actually on.
    const docHref = () => uniqueItemById(getUserMenuItems(), "documentation").href;

    // Hoot's mocked server deliberately reports a series that is NOT this branch's
    // (`serverState.serverVersion` defaults to [1, 0, 0, "final", 0, ""],
    // web/static/tests/_framework/mock_server_state.hoot.js:70), so a re-pinned "19.0" fails here
    // instead of shipping. The expectation is read from serverState - the harness's own
    // declaration of which server is running - rather than from a second hardcoded literal, which
    // would just relocate the footgun into the test.
    expect(docHref()).toBe(
        `https://viindoo.com/documentation/${serverState.serverVersion.slice(0, 2).join(".")}/`
    );

    // ...and it must TRACK the server rather than merely coincide with one value. Restating the
    // running server by direct assignment mid-test is core's own idiom, and core documents that it
    // propagates: "the modification of the serverState will force the re-creation of the user with
    // the new values" (web/static/tests/core/user.test.js:43-46). The mechanism: the assignment
    // goes through serverState's `set` trap, which calls `notifySubscribers()`
    // (mock_server_state.hoot.js:148, :157); that re-runs `makeSession(serverState)` and
    // redefines its properties onto the LIVE session object in place (:21-27), because
    // `@web/session`'s mock registers itself as a subscriber
    // (mock_session.hoot.js:74 -> onServerStateChange, mock_server_state.hoot.js:129-136).
    // `documentationItem` re-reads `session.server_version_info` on every call, so the next
    // `docHref()` sees the new series. The global `beforeEach(applyDefaults)` (:163) restores the
    // default for the following test.
    serverState.serverVersion = [22, 3, 0, "final", 0, ""];
    expect(docHref()).toBe("https://viindoo.com/documentation/22.3/");
});
