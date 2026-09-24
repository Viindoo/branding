/** @odoo-module **/

import {
    animationFrame,
    beforeEach,
    describe,
    expect,
    getActiveElement,
    getFixture,
    mockTouch,
    press,
    queryOne,
    test,
} from "@odoo/hoot";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import {
    defineMenus,
    defineModels,
    fields,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";

// Type-to-search on the flat home menu (ViinHomeMenu): a user must be able to start typing the
// instant the screen is up, in EITHER render shape this component supports - the boot-landing
// client action (no `close` prop) and the navbar overlay (`close` prop set, `isOverlay` true) -
// without clicking the search box first, and without losing whatever they had already typed if
// focus was briefly lost.
//
// This file exercises TWO delivery mechanisms `ViinHomeMenu` owns: a mount-time pre-focus of the
// search input (skipped on a touch device - popping the on-screen keyboard uninvited on a screen
// the user has not touched yet would be worse than leaving it unfocused), and a window-level
// keydown listener (`onWindowKeydown`, wired via `useExternalListener(window, "keydown", ...)`)
// that RECOVERS focus whenever it was lost. That listener is FOCUS-ONLY: it moves focus to the
// search box and lets the browser's own default action deliver the keystroke natively, rather than
// reading `ev.key` and hand-inserting it - which is what makes a keystroke APPEND to content
// already in the box instead of overwriting it, and is also what keeps a composition-based IME
// session from being interrupted by a synthetic value assignment outside its own session.
//
// The guard-condition tests mirror core's OWN editable-protection rule
// (web/static/src/core/hotkeys/hotkey_service.js: `targetIsEditable` accepts
// input/textarea/contenteditable and excludes checkbox/radio; `shouldProtectEditable` adds that
// gate on top of the authorized-key check) and core's own IME-guard TEST TECHNIQUE
// (web/static/tests/core/hotkey_sevice.test.js "should ignore when IME is composing" -
// `press(key, { isComposing: true })`).
//
// WHAT THESE TESTS DO NOT AND CANNOT PROVE. Hoot's `press()` and a browser tour's synthetic
// `dispatchEvent` cannot reproduce a real OS/IME composition SESSION (Windows Telex/VNI, macOS
// Vietnamese, TSF-based) - only a live browser driven by a real input method can. What is asserted
// below is the mechanism (focus-then-native-delivery, append-not-overwrite, mount-time pre-focus
// with its touch guard) and the guard conditions around it; a real IME composition session
// surviving correctly remains a live-browser/live-OS verification outside what this automated
// suite can close.

class ResUsers extends mailModels.ResUsers {
    viin_home_app_order = fields.Char();
}
defineModels({ ...mailModels, ResUsers });

/** @returns {HTMLInputElement} */
function searchInput() {
    return queryOne(".o_viin_home_search_input");
}

/**
 * Mount the real ViinHomeMenu client action (looked up from the SAME "actions" registry entry
 * production code registers it under - never a second copy of the reference).
 * `props.close` set reproduces the navbar-overlay render shape (`isOverlay` true); omitted
 * reproduces the boot-landing client-action shape.
 */
async function mountHomeMenu(props = {}) {
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
    const ViinHomeMenu = registry.category("actions").get("viin_home_menu");
    const component = await mountWithCleanup(ViinHomeMenu, { props });
    await animationFrame(); // let onWillStart's activity/order reads settle
    return component;
}

/** Dispatch a raw, fully-controlled keydown carrying an explicit modifier flag - used where the
 *  assertion only needs the event to REACH the guard (it must be rejected before any insertion
 *  logic runs), not to simulate real typing. Bubbles from whatever currently has focus, exactly
 *  like a real keystroke would. */
function dispatchKeydown(init) {
    const target = getActiveElement();
    const event = new KeyboardEvent("keydown", { key: "a", bubbles: true, cancelable: true, ...init });
    target.dispatchEvent(event);
    return event;
}

describe("ViinHomeMenu type-to-search", () => {
    beforeEach(() => {
        defineMenus([{ id: 1 }]);
    });

    test("client-action render: mounting alone (no press, no click) already focuses the search box on a non-touch device", async () => {
        // The title's precondition is "on a non-touch device" - the mobile test preset emulates
        // touch by default, so this must force the non-touch state itself rather than inherit
        // whatever the running preset happens to give. mockTouch(false) covers the
        // matchMedia("(pointer:coarse)") half of hasTouch(), but browser.ontouchstart is a VALUE
        // captured once when the browser module first loads - mockTouch cannot reach it after the
        // fact - so it must also be patched directly, or hasTouch() stays true under the mobile
        // preset regardless of what mockTouch is told.
        mockTouch(false);
        patchWithCleanup(browser, { ontouchstart: undefined });
        await mountHomeMenu();

        expect(getActiveElement()).toBe(searchInput(), {
            message:
                "the search box must already be focused the moment the boot-landing home menu " +
                "mounts, before any keystroke or click.",
        });
    });

    test("overlay render: mounting alone (no press, no click, no autofocusSearch prop) already focuses the search box on a non-touch device", async () => {
        // Same non-touch precondition as the client-action render test above - the mobile preset
        // emulates touch by default, so this must be forced rather than inherited from the preset.
        // Same two-line requirement too: mockTouch(false) only reaches the matchMedia half of
        // hasTouch(); browser.ontouchstart is a value captured once at module load, so it must be
        // patched directly as well, or hasTouch() stays true under the mobile preset.
        mockTouch(false);
        patchWithCleanup(browser, { ontouchstart: undefined });
        await mountHomeMenu({ close: () => {} });

        expect(getActiveElement()).toBe(searchInput(), {
            message:
                "the search box must already be focused the moment the navbar overlay mounts, " +
                "independent of any autofocusSearch prop, before any keystroke or click.",
        });
    });

    test("a touch device never autofocuses the search box on mount - REGRESSION GUARD for the desktop-only pre-focus", async () => {
        mockTouch(true);
        await mountHomeMenu({ close: () => {} });

        expect(getActiveElement()).not.toBe(searchInput(), {
            message:
                "a touch device must never autofocus the search box on mount - popping the " +
                "on-screen keyboard on a screen the user has not touched yet is unwanted.",
        });

        // Only the MOUNT-TIME pre-focus is touch-gated (hasTouch() guard in home_menu.js); the
        // keydown-recovery path (onWindowKeydown) carries no such guard, so a touch device must
        // still be able to reach type-ahead through it once a keystroke arrives.
        await press("a");
        await animationFrame();

        expect(getActiveElement()).toBe(searchInput(), {
            message:
                "a touch device must still reach the search box through the keydown-recovery " +
                "path - only the mount-time pre-focus is skipped, not type-ahead itself.",
        });
        expect(searchInput().value).toBe("a", {
            message: "the keystroke that recovered focus must also land in the search box.",
        });
    });

    test("a keystroke after focus is lost APPENDS to content already in the search box, never overwrites it", async () => {
        await mountHomeMenu();
        searchInput().focus();
        await press("a");
        await press("b");
        await animationFrame();
        expect(searchInput().value).toBe("ab");

        searchInput().blur();
        await animationFrame();
        expect(getActiveElement()).not.toBe(searchInput());

        await press("c");
        await animationFrame();

        expect(getActiveElement()).toBe(searchInput(), {
            message: "a keystroke after focus is lost must move focus back into the search box.",
        });
        expect(searchInput().value).toBe("abc", {
            message:
                "the keystroke must be APPENDED to what the user had already typed, not replace " +
                'it - a handler that assigns the box\'s value directly would overwrite "ab" with ' +
                "just the new character.",
        });
    });

    test("a checkbox holding focus does not block type-ahead (checkboxes are excluded from editable-protection, mirroring core's own hotkey rule)", async () => {
        await mountHomeMenu();
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        getFixture().appendChild(checkbox);
        checkbox.focus();

        await press("a");
        await animationFrame();

        expect(getActiveElement()).toBe(searchInput(), {
            message: "a focused checkbox must not be treated as an editable that blocks type-ahead.",
        });
        expect(searchInput().value).toBe("a");
    });

    test("an already-focused OTHER input keeps its own keystroke - the search box is not hijacked", async () => {
        await mountHomeMenu();
        const other = document.createElement("input");
        other.type = "text";
        getFixture().appendChild(other);
        other.focus();

        await press("a");
        await animationFrame();

        expect(getActiveElement()).toBe(other, {
            message: "an already-focused unrelated input must keep focus - typing must not hijack it into the search box.",
        });
        expect(searchInput().value).toBe("", {
            message: "the search box must stay untouched while a different input is being typed into.",
        });
        expect(other.value).toBe("a", {
            message: "the already-focused input's own native typing must proceed unaffected.",
        });
    });

    test("continuing to type while the search box itself already has focus adds exactly one character per keystroke - never a double-inject or a re-focus", async () => {
        await mountHomeMenu();
        searchInput().focus();

        await press("a");
        await press("b");
        await animationFrame();

        expect(getActiveElement()).toBe(searchInput());
        expect(searchInput().value).toBe("ab", {
            message:
                "each keystroke while the search box is already focused must add exactly one " +
                "character - a handler that also fires while it is already focused would double it up.",
        });
    });

    test("a keydown fired mid-IME-composition is ignored entirely", async () => {
        await mountHomeMenu();
        searchInput().blur();
        await animationFrame();

        await press("a", { isComposing: true });
        await animationFrame();

        expect(getActiveElement()).not.toBe(searchInput());
        expect(searchInput().value).toBe("");
    });

    test("a keydown reporting the legacy IME keyCode 229 is ignored entirely", async () => {
        await mountHomeMenu();
        searchInput().blur();
        await animationFrame();

        const event = new KeyboardEvent("keydown", { key: "a", bubbles: true, cancelable: true });
        Object.defineProperty(event, "keyCode", { get: () => 229, configurable: true });
        getActiveElement().dispatchEvent(event);
        await animationFrame();

        expect(getActiveElement()).not.toBe(searchInput());
        expect(searchInput().value).toBe("");
    });

    test("a keydown carrying an accelerator modifier (ctrl / alt / meta) is ignored entirely", async () => {
        await mountHomeMenu();
        searchInput().blur();
        await animationFrame();

        dispatchKeydown({ ctrlKey: true });
        dispatchKeydown({ altKey: true });
        dispatchKeydown({ metaKey: true });
        await animationFrame();

        expect(getActiveElement()).not.toBe(searchInput(), {
            message: "a keydown with ctrlKey/altKey/metaKey set must never trigger type-ahead.",
        });
        expect(searchInput().value).toBe("");
    });

    test("the Cmd-K hint badge is not in the rendered markup (superseded by direct type-to-search)", async () => {
        await mountHomeMenu();

        expect(".o_viin_home_menu .o_viin_home_search_hint").toHaveCount(0);
    });
});
