const APPS_BTN_SELECTOR = ".o_frontend_to_backend_apps_btn";
const APPS_BTN_ICON_SELECTOR = "i.oi";
const APPS_BTN_PENDING_ICON = "progress_activity";

// Holds the icon the button shows when idle while it shows the pending one; its presence also tells
// that the button is pending.
export const APPS_BTN_IDLE_ICON_ATTR = "data-viin-idle-icon";

/**
 * A modifier-held or non-primary-button click opens the target in a new tab (or does not
 * navigate at all), so the current page must not show the pending icon.
 */
export function isNewTabClick(ev) {
    return Boolean(ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey || ev.button !== 0);
}

// The anchor is a flex box: the spin class goes on its icon child, never on the anchor itself, or
// the whole button would rotate. Idempotent, so a second click before the reset keeps the idle icon.
export function markAppsBtnPending(el) {
    const iconEl = el.querySelector(APPS_BTN_ICON_SELECTOR);
    if (!iconEl || iconEl.hasAttribute(APPS_BTN_IDLE_ICON_ATTR)) {
        return;
    }
    iconEl.setAttribute(APPS_BTN_IDLE_ICON_ATTR, iconEl.dataset.icon);
    iconEl.dataset.icon = APPS_BTN_PENDING_ICON;
    iconEl.classList.add("oi-spin");
}

// Safe on a button that was never clicked: a bfcache pageshow can fire with no pending icon.
export function resetAppsBtnIcon(el) {
    const iconEl = el.querySelector(APPS_BTN_ICON_SELECTOR);
    if (!iconEl?.hasAttribute(APPS_BTN_IDLE_ICON_ATTR)) {
        return;
    }
    iconEl.dataset.icon = iconEl.getAttribute(APPS_BTN_IDLE_ICON_ATTR);
    iconEl.removeAttribute(APPS_BTN_IDLE_ICON_ATTR);
    iconEl.classList.remove("oi-spin");
}

/**
 * The apps button is a sibling of #wrapwrap, which public.interactions never scans, so a
 * delegated document listener handles it. It does nothing on pages without the button, which
 * website.layout renders only for an internal user.
 */
export function onAppsBtnClick(ev) {
    // The target of a dispatched click can be a non-element (document, a text node), and this
    // module loads on every public page: a throw would show in a visitor's console.
    const appsBtnEl = ev.target?.closest?.(APPS_BTN_SELECTOR);
    if (!appsBtnEl || isNewTabClick(ev)) {
        return;
    }
    markAppsBtnPending(appsBtnEl);
}
// A non-primary click dispatches "auxclick" instead of "click".
document.addEventListener("click", onAppsBtnClick);
document.addEventListener("auxclick", onAppsBtnClick);

window.addEventListener("pageshow", (ev) => {
    // Only a bfcache restore keeps the DOM, and the pending icon, from before the page was left.
    if (!ev.persisted) {
        return;
    }
    const appsBtnEl = document.querySelector(APPS_BTN_SELECTOR);
    if (appsBtnEl) {
        resetAppsBtnIcon(appsBtnEl);
    }
});
