import { describe, expect, getFixture, test } from "@odoo/hoot";
import { click, middleClick, queryOne } from "@odoo/hoot-dom";

import {
    isNewTabClick,
    markAppsBtnPending,
    onAppsBtnClick,
    resetAppsBtnIcon,
} from "@viin_brand_website/js/frontend_to_backend_apps_btn";

describe.current.tags("interaction_dev");

const IDLE_ICON = "apps";
const PENDING_ICON = "progress_activity";

function appsBtnEl() {
    return queryOne(".o_frontend_to_backend_apps_btn");
}

function iconOf(anchorEl) {
    return anchorEl.querySelector("i.oi");
}

// The apps button is mounted without a #wrapwrap around it, as website.layout renders it as a
// sibling of #wrapwrap, with the icon as its child.
function appsBtnHtml() {
    return `
        <a href="/odoo" class="o_frontend_to_backend_apps_btn" title="Go to your Viindoo Apps">
            <i class="oi oi-lg" data-icon="${IDLE_ICON}" aria-hidden="true"/>
        </a>
    `;
}

function mountAppsBtn() {
    getFixture().innerHTML = appsBtnHtml();
}

function detachedAppsBtn() {
    const anchorEl = document.createElement("a");
    anchorEl.className = "o_frontend_to_backend_apps_btn";
    anchorEl.innerHTML = '<i class="oi oi-lg" data-icon="apps" aria-hidden="true"></i>';
    return anchorEl;
}

function isPending(anchorEl) {
    return iconOf(anchorEl).dataset.icon === PENDING_ICON;
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

test("marking the apps button pending spins its icon, and never the button itself", () => {
    const anchorEl = detachedAppsBtn();

    markAppsBtnPending(anchorEl);

    expect(iconOf(anchorEl).dataset.icon).toBe(PENDING_ICON);
    expect(iconOf(anchorEl)).toHaveClass("oi-spin");
    // The anchor is a flex box: a spin class on it would rotate the whole button.
    expect(anchorEl).not.toHaveClass("oi-spin");
});

test("marking an already-pending apps button pending again keeps the idle icon to come back to", () => {
    const anchorEl = detachedAppsBtn();

    markAppsBtnPending(anchorEl);
    markAppsBtnPending(anchorEl);
    resetAppsBtnIcon(anchorEl);

    expect(iconOf(anchorEl).dataset.icon).toBe(IDLE_ICON);
});

test("resetting a pending apps button restores the idle icon and stops the spin", () => {
    const anchorEl = detachedAppsBtn();
    markAppsBtnPending(anchorEl);

    resetAppsBtnIcon(anchorEl);

    expect(iconOf(anchorEl).dataset.icon).toBe(IDLE_ICON);
    expect(iconOf(anchorEl)).not.toHaveClass("oi-spin");
});

test("resetting a never-clicked apps button leaves it untouched and does not throw", () => {
    // pageshow fires on every navigation, so a button that never was pending must be tolerated.
    const anchorEl = detachedAppsBtn();
    const htmlBefore = anchorEl.outerHTML;

    expect(() => resetAppsBtnIcon(anchorEl)).not.toThrow();

    expect(anchorEl.outerHTML).toBe(htmlBefore);
});

test("the apps button keeps an accessible name while its icon is pending", () => {
    const anchorEl = detachedAppsBtn();
    anchorEl.setAttribute("title", "Go to your Viindoo Apps");

    markAppsBtnPending(anchorEl);

    expect(anchorEl.getAttribute("title")).not.toBe("");
});

test("a plain left click marks the apps button pending, without spinning the button itself", async () => {
    mountAppsBtn();

    await click(appsBtnEl());

    expect(isPending(appsBtnEl())).toBe(true);
    expect(iconOf(appsBtnEl())).toHaveClass("oi-spin");
    expect(appsBtnEl()).not.toHaveClass("oi-spin");
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

    for (const modifier of ["ctrlKey", "metaKey", "shiftKey", "altKey"]) {
        await click(appsBtnEl(), { eventInit: { click: { [modifier]: true } } });
        expect(isPending(appsBtnEl())).toBe(false);
    }
});

test("a middle click leaves the apps button icon unchanged", async () => {
    // A middle-button press dispatches "auxclick", which the handler must ignore as well.
    mountAppsBtn();

    await middleClick(appsBtnEl());

    expect(isPending(appsBtnEl())).toBe(false);
});

test("a back/forward-cache restore resets a pending apps button to its idle icon", async () => {
    mountAppsBtn();

    // Reach the pending state through the click handler, as a user does.
    await click(appsBtnEl());
    expect(isPending(appsBtnEl())).toBe(true);

    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));

    expect(iconOf(appsBtnEl()).dataset.icon).toBe(IDLE_ICON);
    expect(iconOf(appsBtnEl())).not.toHaveClass("oi-spin");
});

test("a back/forward-cache restore on an apps button that was never clicked leaves it untouched", async () => {
    // A bfcache restore can land on a page whose button was never clicked.
    mountAppsBtn();
    const htmlBefore = appsBtnEl().outerHTML;

    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));

    expect(appsBtnEl().outerHTML).toBe(htmlBefore);
});

test("an ordinary pageshow that is not a cache restore leaves a pending apps button unchanged", async () => {
    mountAppsBtn();

    await click(appsBtnEl());
    expect(isPending(appsBtnEl())).toBe(true);

    // persisted: false is an ordinary pageshow, which must not reset the pending state.
    window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: false }));

    expect(isPending(appsBtnEl())).toBe(true);
    expect(iconOf(appsBtnEl())).toHaveClass("oi-spin");
});
