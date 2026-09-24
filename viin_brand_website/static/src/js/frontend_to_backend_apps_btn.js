const APPS_BTN_SELECTOR = ".o_frontend_to_backend_apps_btn";

export const APPS_BTN_STATIC_ICON_CLASS = "fa-th";
export const APPS_BTN_SPINNER_MARKER_CLASS = "o_viin_apps_btn_spinner";
// A marker class - not the shared fa-circle-o-notch/fa-spin glyph classes, which other spinners
// on the page may also carry - lets markAppsBtnPending/resetAppsBtnIcon target exactly this
// spinner without depending on which icon font drew it.
export const APPS_BTN_SPINNER_CLASSES = [
    "fa",
    "fa-circle-o-notch",
    "fa-spin",
    APPS_BTN_SPINNER_MARKER_CLASS,
];

/**
 * A modifier-held or non-primary-button click opens the target in a new tab (or does not
 * navigate at all), so the current page's own navigation - and the pending-icon feedback tied
 * to it - must not fire.
 */
export function isNewTabClick(ev) {
    return Boolean(ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey || ev.button !== 0);
}

// The anchor itself carries layout classes (d-flex/align-items-center/justify-content-center)
// besides its icon glyph, so fa-spin on the anchor rotates that whole flex box - background and
// padding included - instead of only the icon; the spinner is therefore a dedicated child
// element that carries nothing but the spin classes.
// Idempotent: a second click before the reset must not append a duplicate spinner child.
export function markAppsBtnPending(el) {
    if (el.querySelector(`.${APPS_BTN_SPINNER_MARKER_CLASS}`)) {
        return;
    }
    el.classList.remove(APPS_BTN_STATIC_ICON_CLASS);
    const spinnerEl = document.createElement("i");
    spinnerEl.classList.add(...APPS_BTN_SPINNER_CLASSES);
    spinnerEl.setAttribute("role", "img");
    spinnerEl.setAttribute("aria-label", "Loading");
    spinnerEl.setAttribute("title", "Loading");
    el.appendChild(spinnerEl);
}

// Safe on a button that was never clicked - a bfcache pageshow can fire with no pending
// spinner present.
export function resetAppsBtnIcon(el) {
    const spinnerEl = el.querySelector(`.${APPS_BTN_SPINNER_MARKER_CLASS}`);
    if (spinnerEl) {
        spinnerEl.remove();
    }
    el.classList.add(APPS_BTN_STATIC_ICON_CLASS);
}

/**
 * website.layout renders the apps button as a sibling of #wrapwrap, never a descendant of it
 * (views/website_templates.xml's own xpath only edits attributes on core's anchor, it does not
 * relocate it) - so the public.interactions scanner, which only ever walks #wrapwrap (or body when
 * #wrapwrap is absent), can never reach it. A delegated document listener is used instead: it
 * needs no ancestor the button might not have, and still no-ops harmlessly - via closest() - on
 * every page where the button (rendered only for an internal user) is absent.
 */
export function onAppsBtnClick(ev) {
    // A dispatched click can carry a target that is not an element (document, a text node),
    // and this module loads on every public page of every site - a throw here would surface
    // in a visitor's console.
    const appsBtnEl = ev.target?.closest?.(APPS_BTN_SELECTOR);
    if (!appsBtnEl || isNewTabClick(ev)) {
        return;
    }
    markAppsBtnPending(appsBtnEl);
}
// A non-primary click (middle button, or a modifier held with the primary button) dispatches
// "auxclick" instead of "click" - both are bound to the same guarded handler.
document.addEventListener("click", onAppsBtnClick);
document.addEventListener("auxclick", onAppsBtnClick);

window.addEventListener("pageshow", (ev) => {
    // Only a bfcache restore (Back/Forward navigation) leaves the DOM - and the apps button's
    // classList - untouched from before the page was left; an ordinary pageshow reflects a
    // freshly rendered page that already has its static icon.
    if (!ev.persisted) {
        return;
    }
    const appsBtnEl = document.querySelector(APPS_BTN_SELECTOR);
    if (appsBtnEl) {
        resetAppsBtnIcon(appsBtnEl);
    }
});
