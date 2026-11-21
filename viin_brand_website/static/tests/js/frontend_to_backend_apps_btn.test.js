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

function appsBtnEl() {
    return queryOne(".o_frontend_to_backend_apps_btn");
}

// The apps-button anchor starts on the static fa-th icon. It is mounted without a #wrapwrap
// around it, as website.layout renders it as a sibling of #wrapwrap.
function mountAppsBtn() {
    getFixture().innerHTML = `
        <a href="/odoo" class="o_frontend_to_backend_apps_btn fa fa-th" title="Go to your Viindoo Apps"></a>
    `;
}

// The spinner child is identified by its marker class, not by the fa-* glyph classes.
function spinnerChildOf(anchorEl) {
    return anchorEl.querySelector(`.${APPS_BTN_SPINNER_MARKER_CLASS}`);
}

function spinnerChildCountOf(anchorEl) {
    return anchorEl.querySelectorAll(`.${APPS_BTN_SPINNER_MARKER_CLASS}`).length;
}

/** The accessible name of an icon-only element: aria-label, else title. */
function accessibleNameOf(el) {
    const ariaLabel = el.getAttribute("aria-label");
    if (ariaLabel && ariaLabel.trim()) {
        return ariaLabel.trim();
    }
    const title = el.getAttribute("title");
    return title ? title.trim() : "";
}

test("a click with no modifier held and the primary button is never classified as opening a new tab", () => {
    expect(
        isNewTabClick({ ctrlKey: false, metaKey: false, shiftKey: false, altKey: false, button: 0 })
    ).toBe(false);
});

test("a modifier-held or non-primary-button click is always classified as opening a new tab", () => {
    // Each case flips exactly one field of the baseline above.
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

test("marking the apps button pending swaps its static icon for a dedicated spinner child, and never spins the button itself", () => {
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn fa fa-th";

    markAppsBtnPending(anchorEl);

    expect(anchorEl).not.toHaveClass("fa-th");
    // The anchor is a flex box: a spin class on it would rotate the whole button.
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
    // pageshow fires on every navigation, so a button that never was pending must be tolerated.
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
    // The click only gives feedback; the browser's own navigation to href must proceed.
    // Hoot's window mock prevents the default of any click bubbling to an <a href>, so the handler
    // is called directly with an event object this test owns.
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
    // Ctrl/Cmd/Shift/Alt+click opens /odoo in a new tab, so the page must not show the pending
    // state. hoot-dom reads modifiers from its own keyboard state, so they are passed through
    // `eventInit` of the click event.
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
    // A middle-button press dispatches "auxclick", which the handler must ignore as well.
    mountAppsBtn();

    await middleClick(appsBtnEl());

    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);
});

test("a back/forward-cache restore resets a pending apps button to its static icon", async () => {
    mountAppsBtn();

    // Reach the pending state through the click handler, as a user does.
    await click(appsBtnEl());
    expect(appsBtnEl()).not.toHaveClass("fa-th");

    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));

    expect(appsBtnEl()).toHaveClass("fa-th");
    expect(spinnerChildOf(appsBtnEl())).toBe(null);
});

test("a back/forward-cache restore on an apps button that was never clicked leaves it untouched", async () => {
    // A bfcache restore can land on a page whose button was never clicked.
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

    // persisted: false is an ordinary pageshow, which must not reset the pending state.
    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: false }));

    expect(appsBtnEl()).not.toHaveClass("fa-th");
    const spinnerEl = spinnerChildOf(appsBtnEl());
    expect(spinnerEl).not.toBe(null);
    expect(spinnerEl).toHaveClass("fa-circle-o-notch");
    expect(spinnerEl).toHaveClass("fa-spin");
});
