const APPS_BTN_SELECTOR = ".o_frontend_to_backend_apps_btn";
const APPS_BTN_STATIC_ICON_CLASS = "fa-th";

// Identifies this spinner without relying on the shared fa-circle-o-notch/fa-spin classes, which
// other spinners on the page also carry.
export const APPS_BTN_SPINNER_MARKER_CLASS = "o_viin_apps_btn_spinner";

/**
 * A modifier-held or non-primary-button click opens the target in a new tab (or does not
 * navigate at all), so the current page must not show the pending icon.
 */
export function isNewTabClick(ev) {
    return Boolean(ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey || ev.button !== 0);
}

// The spinner is a dedicated child: the anchor is a flex box, so fa-spin on the anchor itself
// would rotate the whole button instead of the icon. Idempotent, so a second click before the
// reset adds no second spinner.
export function markAppsBtnPending(el) {
    if (el.querySelector(`.${APPS_BTN_SPINNER_MARKER_CLASS}`)) {
        return;
    }
    el.classList.remove(APPS_BTN_STATIC_ICON_CLASS);
    const spinnerEl = document.createElement("i");
    spinnerEl.classList.add("fa", "fa-circle-o-notch", "fa-spin", APPS_BTN_SPINNER_MARKER_CLASS);
    spinnerEl.setAttribute("role", "img");
    spinnerEl.setAttribute("aria-label", "Loading");
    spinnerEl.setAttribute("title", "Loading");
    el.appendChild(spinnerEl);
}

// Safe on a button that was never clicked: a bfcache pageshow can fire with no spinner present.
export function resetAppsBtnIcon(el) {
    const spinnerEl = el.querySelector(`.${APPS_BTN_SPINNER_MARKER_CLASS}`);
    if (spinnerEl) {
        spinnerEl.remove();
    }
    el.classList.add(APPS_BTN_STATIC_ICON_CLASS);
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
    // Only a bfcache restore keeps the DOM, and the spinner, from before the page was left.
    if (!ev.persisted) {
        return;
    }
    const appsBtnEl = document.querySelector(APPS_BTN_SELECTOR);
    if (appsBtnEl) {
        resetAppsBtnIcon(appsBtnEl);
    }
});
