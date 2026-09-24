import { describe, expect, getFixture, test } from "@odoo/hoot";
import { click, middleClick, queryOne } from "@odoo/hoot-dom";

import {
    APPS_BTN_SPINNER_MARKER_CLASS,
    isNewTabClick,
    markAppsBtnPending,
    onAppsBtnClick,
    resetAppsBtnIcon,
} from "@viin_brand_website/js/frontend_to_backend_apps_btn";

describe.current.tags("interaction_dev");

// Matches the frontend header's real markup: website.layout's own apps-button anchor always
// starts on the static fa-th icon (see this module's website_templates.xml inherit_id
// website.layout xpath). Mounted directly into the Hoot fixture with no #wrapwrap around it -
// the button's own production ancestry (website.layout renders it as a #wrapwrap SIBLING, never
// a descendant) - so a regression that goes back to depending on #wrapwrap fails here too.
const APPS_BTN_HTML = `
    <a href="/odoo" class="o_frontend_to_backend_apps_btn fa fa-th" title="Go to your Viindoo Apps"></a>
`;

function appsBtnEl() {
    return queryOne(".o_frontend_to_backend_apps_btn");
}

function mountAppsBtn() {
    getFixture().innerHTML = APPS_BTN_HTML;
}

// The spinner is a dedicated child, identified by its marker class - never by the fa-* glyph
// classes it also carries, since those are a rendering detail the marker must stay independent
// of (see APPS_BTN_SPINNER_MARKER_CLASS's own contract).
function spinnerChildOf(anchorEl) {
    return anchorEl.querySelector(`.${APPS_BTN_SPINNER_MARKER_CLASS}`);
}

function spinnerChildCountOf(anchorEl) {
    return anchorEl.querySelectorAll(`.${APPS_BTN_SPINNER_MARKER_CLASS}`).length;
}

/**
 * The accessible name of an icon-only element (no visible text, no wrapping <label>): an
 * explicit aria-label wins; title is the remaining fallback the ARIA accessible-name
 * computation itself falls back to for an element with neither.
 */
function accessibleNameOf(el) {
    const ariaLabel = el.getAttribute("aria-label");
    if (ariaLabel && ariaLabel.trim()) {
        return ariaLabel.trim();
    }
    const title = el.getAttribute("title");
    return title ? title.trim() : "";
}

// --- pure-function coverage: no DOM wiring involved -------------------------------------------

test("a click with no modifier held and the primary button is never classified as opening a new tab", () => {
    expect(
        isNewTabClick({ ctrlKey: false, metaKey: false, shiftKey: false, altKey: false, button: 0 })
    ).toBe(false);
});

test("a modifier-held or non-primary-button click is always classified as opening a new tab", () => {
    // Each case below flips exactly ONE field away from the all-false/button-0 baseline that the
    // previous test proves is NOT a new-tab click - so this is the minimal matrix that catches an
    // implementation checking only a subset of the four modifiers or ignoring the button field.
    expect(
        isNewTabClick({ ctrlKey: true, metaKey: false, shiftKey: false, altKey: false, button: 0 })
    ).toBe(true);
    expect(
        isNewTabClick({ ctrlKey: false, metaKey: true, shiftKey: false, altKey: false, button: 0 })
    ).toBe(true);
    expect(
        isNewTabClick({ ctrlKey: false, metaKey: false, shiftKey: true, altKey: false, button: 0 })
    ).toBe(true);
    expect(
        isNewTabClick({ ctrlKey: false, metaKey: false, shiftKey: false, altKey: true, button: 0 })
    ).toBe(true);
    expect(
        isNewTabClick({ ctrlKey: false, metaKey: false, shiftKey: false, altKey: false, button: 1 })
    ).toBe(true);
});

// --- icon-shape coverage: markAppsBtnPending/resetAppsBtnIcon called directly, no listener -----
// wiring involved. A dedicated child carries the spinner; the anchor - which core also styles as
// a flex box - must never carry a spin class itself, or the whole box rotates again.

test("marking the apps button pending swaps its static icon for a dedicated spinner child, and never spins the button itself", () => {
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn fa fa-th";

    markAppsBtnPending(anchorEl);

    expect(anchorEl).not.toHaveClass("fa-th");
    // Regression guard: this is the owner's exact defect - fa-spin landed on this anchor, which
    // core also renders as a flex box, so rotating the icon rotated the whole button.
    expect(anchorEl).not.toHaveClass("fa-spin");
    expect(anchorEl).not.toHaveClass("fa-circle-o-notch");

    const spinnerEl = spinnerChildOf(anchorEl);
    expect(spinnerEl).not.toBe(null);
    expect(spinnerEl).toHaveClass("fa");
    expect(spinnerEl).toHaveClass("fa-circle-o-notch");
    expect(spinnerEl).toHaveClass("fa-spin");
});

test("marking an already-pending apps button pending again does not add a second spinner", () => {
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn fa fa-th";

    markAppsBtnPending(anchorEl);
    markAppsBtnPending(anchorEl);

    expect(spinnerChildCountOf(anchorEl)).toBe(1);
});

test("resetting a pending apps button removes the spinner child and restores the static icon", () => {
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn fa fa-th";
    markAppsBtnPending(anchorEl);

    resetAppsBtnIcon(anchorEl);

    expect(anchorEl).toHaveClass("fa-th");
    expect(anchorEl).not.toHaveClass("fa-circle-o-notch");
    expect(anchorEl).not.toHaveClass("fa-spin");
    expect(spinnerChildOf(anchorEl)).toBe(null);
});

test("resetting a never-clicked apps button leaves it untouched and does not throw", () => {
    // pageshow fires on every navigation, including one where this button's own click handler
    // never ran - resetAppsBtnIcon must tolerate a button that never entered the pending state.
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn fa fa-th";
    const classNameBefore = anchorEl.className;

    expect(() => resetAppsBtnIcon(anchorEl)).not.toThrow();

    expect(anchorEl.className).toBe(classNameBefore);
    expect(spinnerChildOf(anchorEl)).toBe(null);
});

test("the spinner child carries an accessible name, since the grid glyph it replaces is gone", () => {
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn fa fa-th";

    markAppsBtnPending(anchorEl);

    expect(accessibleNameOf(spinnerChildOf(anchorEl))).not.toBe("");
});

// --- behaviour coverage: the module's own document/window listeners, on a real DOM element ----

test("a plain left click marks the apps button pending, without spinning the button itself", async () => {
    mountAppsBtn();

    await click(appsBtnEl());

    expect(appsBtnEl()).not.toHaveClass("fa-th");
    expect(appsBtnEl()).not.toHaveClass("fa-spin");
    expect(appsBtnEl()).not.toHaveClass("fa-circle-o-notch");

    const spinnerEl = spinnerChildOf(appsBtnEl());
    expect(spinnerEl).not.toBe(null);
    expect(spinnerEl).toHaveClass("fa-circle-o-notch");
    expect(spinnerEl).toHaveClass("fa-spin");
});

test("the click handler never cancels the browser's own navigation to href", async () => {
    // /odoo can lag on an install with many modules - the click only gives feedback, it must
    // never itself block the browser's own navigation to href. A real click() cannot measure
    // this here: Hoot's own window mock (onAnchorHrefClick, wired up by setupWindow before every
    // test) always calls preventDefault on a dispatched click that bubbles to an <a href>, to
    // keep the test runner from actually navigating - so defaultPrevented on that event reflects
    // that mock, not this handler, on every run regardless of what this handler does. Calling the
    // exported handler directly with an event object this test owns - one never fed through the
    // DOM dispatcher - is the only way to observe this handler's own effect on the event.
    mountAppsBtn();

    const ev = {
        target: appsBtnEl(),
        ctrlKey: false,
        metaKey: false,
        shiftKey: false,
        altKey: false,
        button: 0,
        defaultPrevented: false,
        preventDefault() {
            this.defaultPrevented = true;
        },
    };
    onAppsBtnClick(ev);

    expect(ev.defaultPrevented).toBe(false);
});

test("a click with a modifier key held leaves the apps button icon unchanged", async () => {
    // Ctrl/Cmd/Shift/Alt+click opens /odoo in a NEW tab; the page under the user's eyes never
    // navigates, so its icon must never enter the pending state - unlike the plain-click test
    // above, which proves the opposite outcome for the unmodified case.
    //
    // hoot-dom's click() only forwards `options.button` straight onto the dispatched event;
    // every other modifier field it reads from the keyboard state it tracks itself (toggled by
    // press()/keyDown()), never from a bare option like `{ ctrlKey: true }` - so the modifier has
    // to be routed through `eventInit`, keyed by the event type it must land on, which is the one
    // channel hoot-dom merges onto the dispatched event untouched.
    mountAppsBtn();

    await click(appsBtnEl(), { eventInit: { click: { ctrlKey: true } } });
    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);

    await click(appsBtnEl(), { eventInit: { click: { metaKey: true } } });
    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);

    await click(appsBtnEl(), { eventInit: { click: { shiftKey: true } } });
    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);

    await click(appsBtnEl(), { eventInit: { click: { altKey: true } } });
    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);
});

test("a middle click leaves the apps button icon unchanged", async () => {
    // A genuine middle-button press dispatches "auxclick", never "click" (UI Events spec, and
    // hoot-dom's own middleClick() helper dispatches exactly that) - so this only proves the
    // guard clause itself if the handler is ALSO wired to auxclick; a build that forgot that
    // wiring, or that forgot the button check inside the shared handler, both fail this the same
    // way a build with the check simply inverted would.
    mountAppsBtn();

    await middleClick(appsBtnEl());

    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);
});

test("a back/forward-cache restore resets a pending apps button to its static icon", async () => {
    mountAppsBtn();

    // Arrange: reach the pending state the same way a real user would, through the click handler
    // itself, not by hand-setting classList - so this test still fails if the click handler stops
    // producing that state.
    await click(appsBtnEl());
    expect(appsBtnEl()).not.toHaveClass("fa-th");

    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));

    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);
});

test("a back/forward-cache restore on an apps button that was never clicked leaves it untouched", async () => {
    // The listener runs unconditionally on every persisted pageshow - a bfcache restore can land
    // on a page where this particular button was never clicked before the user navigated away.
    mountAppsBtn();
    const classNameBefore = appsBtnEl().className;

    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));

    expect(appsBtnEl().className).toBe(classNameBefore);
    expect(spinnerChildOf(appsBtnEl())).toBe(null);
});

test("an ordinary pageshow that is not a cache restore leaves a pending apps button unchanged", async () => {
    mountAppsBtn();

    await click(appsBtnEl());
    expect(appsBtnEl()).not.toHaveClass("fa-th");

    // persisted: false is what an ordinary (non-bfcache) pageshow carries - this must NOT trigger
    // the same reset as the test above, or persisted would never actually be consulted.
    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: false }));

    expect(appsBtnEl()).not.toHaveClass("fa-th");
    const spinnerEl = spinnerChildOf(appsBtnEl());
    expect(spinnerEl).not.toBe(null);
    expect(spinnerEl).toHaveClass("fa-circle-o-notch");
    expect(spinnerEl).toHaveClass("fa-spin");
});
