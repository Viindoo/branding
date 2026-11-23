import { beforeEach, describe, expect, test } from "@odoo/hoot";

// Core registers its stock user-menu entries as a plain module side effect
// (web/static/src/webclient/user_menu/user_menu_items.js): "support", "shortcuts", "separator",
// "preferences", "install_pwa", "log_out" and "share_url". viin_brand deletes "support" and adds
// Viindoo entries (static/src/webclient/user_menu_item.js). `Registry.remove()` is
// `delete this.content[key]` with no existence check and no throw, so a core rename of the key
// turns the call into a silent no-op. Importing the patch as a side effect runs its registry
// mutation before any test body executes.
import { allowTranslations, mountWithCleanup, serverState } from "@web/../tests/web_test_helpers";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import "@viin_brand/webclient/user_menu_item";

describe.current.tags("desktop");

// Every assertion below reads an item's `description`, which core and this module build with
// `_t(...)`. A suite that loads no localization returns lazy `TranslatedString`s whose `valueOf()`
// throws. `allowTranslations()` flips the loaded flag without injecting any term, so every
// `_t(source)` resolves to `source`, the English text that ships.
beforeEach(() => {
    allowTranslations();
});

// If any test below fails, Odoo's own "Help" entry (pointing at odoo.com support) ships in the
// user menu of a Viindoo-branded build next to the "Support" replacement: two competing support
// links in the same dropdown, one Odoo-branded. Because `Registry.remove()` never throws on a
// missing key, the failure is otherwise silent.
//
// The guards assert on what the user sees: the descriptors the user menu builds, the way core's
// UserMenu does at render time (its factories call hooks, so they run in the component's scope).

/** Build every descriptor the user menu would render. */
async function getUserMenuItems() {
    const userMenu = await mountWithCleanup(UserMenu);
    return userMenu.getElements();
}

/** The single entry the menu offers for a given item id, asserting there is exactly one. */
function uniqueItemById(items, id) {
    const matches = items.filter((item) => item.id === id);
    expect(matches).toHaveLength(1);
    return matches[0];
}

test("no user menu entry may carry Odoo branding", async () => {
    const items = await getUserMenuItems();
    // An empty menu would satisfy the loop below trivially.
    expect(items.length).toBeGreaterThan(0);
    for (const item of items) {
        // `description` is a plain string for most entries, a Markup object for core's shortcuts
        // entry, and absent on the separator, so coerce before matching.
        expect(String(item.description ?? "")).not.toMatch(/odoo\.com/i);
        expect(String(item.href ?? "")).not.toMatch(/odoo\.com/i);
    }
});

test("the user menu must never offer two entries for the same action", async () => {
    // Core's supportItem and ours both build `id: "support"`. A silently no-op `remove()`
    // therefore shows up as a duplicate id, the production symptom of an Odoo-branded entry
    // beside its Viindoo replacement, without depending on any registry key name. The id
    // alignment is load-bearing: renaming our id to e.g. "viindoo_support" would stop a
    // resurrected stock entry from colliding.
    const ids = (await getUserMenuItems()).map((item) => item.id).filter(Boolean);
    const duplicated = ids.filter((id, index) => ids.indexOf(id) !== index);
    expect(duplicated).toEqual([]);
});

test("the user menu's documentation, support and account entries must point at Viindoo", async () => {
    const items = await getUserMenuItems();
    expect(uniqueItemById(items, "documentation").href).toMatch(/^https:\/\/viindoo\.com\//);
    expect(uniqueItemById(items, "support").href).toMatch(/^https:\/\/viindoo\.com\//);
    expect(uniqueItemById(items, "account").href).toMatch(/^https:\/\/viindoo\.com\//);
});

test("the documentation link must follow the running server's series, never a pinned literal", async () => {
    // A documentation URL that pins its series literal keeps rendering after a move to a new
    // series, and the user lands on the wrong or missing documentation tree. The de-branded link
    // must track the server the user is on.
    //
    // The expectation is read from serverState, the harness's declaration of the running server,
    // not from a second hardcoded literal.
    const docHref = async () => uniqueItemById(await getUserMenuItems(), "documentation").href;
    expect(await docHref()).toBe(
        `https://viindoo.com/documentation/${serverState.serverVersion.slice(0, 2).join(".")}/`
    );
});
