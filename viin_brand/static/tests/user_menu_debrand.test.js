import { beforeEach, describe, expect, test } from "@odoo/hoot";

// Core registers its stock user-menu entries as a plain module side effect
// (web/static/src/webclient/user_menu/user_menu_items.js):
//   "support" -> supportItem, "shortcuts", "separator", "preferences",
//   "odoo_account" -> odooAccountItem, "install_pwa", "log_out".
// viin_brand deletes two of those keys and substitutes Viindoo entries
// (static/src/webclient/user_menu_item.js). `Registry.remove()` is `delete this.content[key]`
// with no existence check and no throw, so a core rename of either key turns both calls into
// silent no-ops. Importing the patch as a side effect runs its registry mutation before any test
// body executes.
import { registry } from "@web/core/registry";
import { allowTranslations, serverState } from "@web/../tests/web_test_helpers";
import { odooAccountItem } from "@web/webclient/user_menu/user_menu_items";
import "@viin_brand/webclient/user_menu_item";

describe.current.tags("headless");

// Every assertion below reads an item's `description`, which core and this module build with
// `_t(...)`. A headless suite loads no localization service, so every `_t()` returns a lazy
// `TranslatedString` whose `valueOf()` throws "Cannot translate string: translations have not been
// loaded". Core's shortcuts entry forces that `valueOf` inside its factory by interpolating
// `_t("Shortcuts")` into a `markup` template, so building the menu would throw before any
// assertion. `allowTranslations()` is core's remedy for this situation.
//
// `allowTranslations()` and not `patchTranslations({...})`: it flips the loaded flag without
// injecting any term, so every `_t(source)` resolves to `source`, the English text that ships.
// Injected terms could launder the "My Odoo.com Account" branding string the sweep below exists to
// catch.
beforeEach(() => {
    allowTranslations();
});

// If any test below fails, Odoo's own "My Odoo.com Account" entry (and its "Help" entry pointing
// at odoo.com support) ships in the user menu of a Viindoo-branded build next to the
// "My Viindoo.com account" / "Support" replacements: two competing account links in the same
// dropdown, one Odoo-branded. Because `Registry.remove()` never throws on a missing key, the
// failure is otherwise silent.
//
// The guards assert on what the user sees (the built menu descriptors) and on core's exported
// factory identity, not on key absence: `get("odoo_account", null) === null` passes vacuously the
// moment core renames the key, which is the drift being guarded against.
//
// A "before the patch" snapshot is not observable in Hoot: the module loader executes every module
// of the suite's addon closure before the test file runs, so the patch is already applied. The
// precondition is asserted against core's registration directly, see "core's own Odoo.com account
// factory" below.

/** Minimal env carrying only what core's item factories read eagerly while building a descriptor:
 * `env.isSmall` (shortcuts), `env.services.menu.getCurrentApp()` (install_pwa) and
 * `env.services.pwa.isScopedApp` (log_out). Every other env access in core's factories lives
 * inside a `callback`/`show` closure that is never invoked here. */
function makeEnv() {
    return {
        isSmall: false,
        services: {
            menu: { getCurrentApp: () => null },
            pwa: { isScopedApp: false },
        },
    };
}

/** Build every descriptor the user menu would render, the way core's UserMenu does at render
 * time: `userMenuRegistry.getAll().map((element) => element(this.env))`. */
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
    // An empty menu would satisfy the loop below trivially.
    expect(items.length).toBeGreaterThan(0);
    for (const item of items) {
        // `description` is a plain string for most entries, a Markup object for core's shortcuts
        // entry, and absent on the separator, so coerce before matching.
        expect(String(item.description ?? "")).not.toMatch(/odoo\.com/i);
        expect(String(item.href ?? "")).not.toMatch(/odoo\.com/i);
    }
});

test("core's own Odoo.com account factory must not survive under any registry key", () => {
    // Precondition: core exports the Odoo-branded account factory it registers under
    // "odoo_account". Odoo's transpiler turns this file's named import into a destructuring
    // `require`, so a core rename of the export would silently bind `undefined` here and make the
    // outcome assertion vacuous; this line makes that case fail loudly.
    expect(odooAccountItem).toBeInstanceOf(Function);

    // Outcome, rename-proof: the exact factory object core registers is not reachable under any
    // key. If core renames "odoo_account", `remove("odoo_account")` no-ops and this factory stays
    // in the registry under the new key.
    expect(registry.category("user_menuitems").getAll()).not.toInclude(odooAccountItem);

    // Weaker companion: pins the key this module deletes. It passes vacuously after a core rename,
    // so it is not the load-bearing assertion.
    expect(registry.category("user_menuitems").get("odoo_account", null)).toBe(null);
});

test("the user menu must never offer two entries for the same action", () => {
    // Core's supportItem and ours both build `id: "support"`; core's odooAccountItem and ours both
    // build `id: "account"`. A silently no-op `remove()` therefore shows up as a duplicate id, the
    // production symptom of an Odoo-branded entry beside its Viindoo replacement, without
    // depending on any registry key name. The id alignment is load-bearing: renaming our ids to
    // e.g. "viindoo_support" would stop a resurrected stock entry from colliding, and core's stock
    // support entry carries no odoo.com href for the branding sweep above to catch (its url is
    // `session.support_url`, which the mocked Hoot session does not define).
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
    // A documentation URL that pins its series literal keeps rendering after a move to a new
    // series, and the user lands on the wrong or missing documentation tree. The de-branded link
    // must track the server the user is on.
    const docHref = () => uniqueItemById(getUserMenuItems(), "documentation").href;

    // Hoot's mocked server reports a series that is not this branch's (`serverState.serverVersion`
    // defaults to [1, 0, 0, "final", 0, ""]), so a re-pinned "19.0" fails here. The expectation is
    // read from serverState, the harness's declaration of the running server, not from a second
    // hardcoded literal.
    expect(docHref()).toBe(
        `https://viindoo.com/documentation/${serverState.serverVersion.slice(0, 2).join(".")}/`
    );

    // The link must track the server rather than coincide with one value. Assigning
    // `serverState.serverVersion` mid-test is core's idiom and propagates: the assignment goes
    // through serverState's `set` trap, which notifies subscribers, and the `@web/session` mock
    // redefines its properties on the live session object. `documentationItem` re-reads
    // `session.server_version_info` on every call, so the next `docHref()` sees the new series. A
    // global `beforeEach` restores the default for the following test.
    serverState.serverVersion = [22, 3, 0, "final", 0, ""];
    expect(docHref()).toBe("https://viindoo.com/documentation/22.3/");
});
