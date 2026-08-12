/** @odoo-module **/

// viin_theme service: the SINGLE source that resolves + persists the backend appearance (dark-mode
// scheme + density). TDD viin-backend-theme §2.1 + §5 (density = the ONE theme-owned functional
// attribute). PR #658 T-1: the SCHEME toggle is persist+reload (dark is a recompiled server bundle),
// while DENSITY stays an instant, reload-free attribute flip.
//
// MECHANISM (grounded against core + the base dark plumbing, no --viin-* anywhere):
//  - Scheme CHOICE (light/dark/auto/"System") is the user preference res.users.viin_color_scheme
//    (SELF_WRITEABLE, so a plain internal user sets their own). It is the source of truth for the
//    radio state; not known synchronously at boot, so it is reconciled via one lightweight SELF-read.
//  - EFFECTIVE scheme (light/dark) is what the server serves. 'auto' resolves to the OS preference
//    via matchMedia("(prefers-color-scheme: dark)").
//  - Scheme toggle = PERSIST + RELOAD (PR #658 C-2/T-1). Dark mode is now the RECOMPILED
//    web.assets_web_dark bundle owned by viin_brand_web - a server-selected bundle cannot swap
//    without a reload - so setScheme persists the EFFECTIVE scheme to the `color_scheme` cookie the
//    server reads (name FIXED by the base ir.http.color_scheme + boot reflection) and the CHOICE to
//    the user field, then reloads. It does NOT instant-flip [data-bs-theme]; on reload the server
//    reads the cookie, serves the dark bundle, and boot-stamps the paint. The boot [data-bs-theme]
//    stamp is kept as a harmless hint (Bootstrap dark component variants); correctness rides the
//    recompiled bundle, not a runtime attribute.
//  - Density CHOICE (comfortable/compact) has no server field: SSOT is the `viin_density` cookie
//    (the server stamps data-viin-density from it FOUC-free). Apply = set
//    documentElement.dataset.viinDensity INSTANTLY (attribute-scoped SCSS, no bundle, no reload);
//    density.scss carries the size rules.

import { registry } from "@web/core/registry";
import { cookie } from "@web/core/browser/cookie";
import { browser } from "@web/core/browser/browser";
import { user } from "@web/core/user";
import { reactive } from "@odoo/owl";

// Cookie names are FIXED by W4a (ir.http.color_scheme + the webclient_bootstrap boot reflection).
// Do NOT rename - the server reads exactly these.
const SCHEME_COOKIE = "color_scheme"; // stores the EFFECTIVE scheme (light|dark)
const DENSITY_COOKIE = "viin_density"; // stores the density choice (comfortable|compact)
const DARK_MEDIA = "(prefers-color-scheme: dark)";

const SCHEMES = ["light", "dark", "auto"]; // user CHOICE (res.users.viin_color_scheme)
const DENSITIES = ["comfortable", "compact"];

/** Resolve a CHOICE to the EFFECTIVE light|dark that actually paints. */
function resolveEffective(choice) {
    if (choice === "dark" || choice === "light") {
        return choice;
    }
    // 'auto' (or anything unknown) follows the device/OS preference.
    return browser.matchMedia(DARK_MEDIA).matches ? "dark" : "light";
}

export const viinThemeService = {
    dependencies: ["orm"],
    start(env, { orm }) {
        const root = document.documentElement;

        // Density: read the FOUC-free cookie the server already stamped; default comfortable.
        const cookieDensity = cookie.get(DENSITY_COOKIE);
        const density = DENSITIES.includes(cookieDensity) ? cookieDensity : "comfortable";

        // Seed the reactive state provisionally from the boot-stamped effective scheme; the true
        // CHOICE (which may be 'auto') is reconciled by the SELF-read below and updates state.scheme.
        const bootEffective = root.dataset.bsTheme === "dark" ? "dark" : "light";
        const state = reactive({ scheme: bootEffective, density });

        // matchMedia listener lifecycle - active ONLY while the choice is 'auto'.
        let mql = null;
        const onOsChange = () => applyEffective("auto");
        function startOsListener() {
            if (!mql) {
                mql = browser.matchMedia(DARK_MEDIA);
                mql.addEventListener("change", onOsChange);
            }
        }
        function stopOsListener() {
            if (mql) {
                mql.removeEventListener("change", onOsChange);
                mql = null;
            }
        }

        // Flip the paint instantly + keep the cookie in sync so a reload and core cookie-widgets agree.
        function applyEffective(choice) {
            const effective = resolveEffective(choice);
            root.dataset.bsTheme = effective;
            cookie.set(SCHEME_COOKIE, effective);
        }
        function applyDensity(value) {
            root.dataset.viinDensity = value;
            cookie.set(DENSITY_COOKIE, value);
        }

        // Reconcile the true CHOICE from the stored preference (SELF-readable). Non-blocking: the
        // boot paint is already correct for explicit light/dark. This is what makes 'auto' work - at
        // boot the server cannot resolve 'auto' (ir.http.color_scheme falls back to light), so once
        // we learn choice === 'auto' we resolve via matchMedia and re-apply (and track OS changes).
        (async () => {
            let choice = bootEffective;
            try {
                const [rec] = await orm.read("res.users", [user.userId], ["viin_color_scheme"]);
                if (rec && SCHEMES.includes(rec.viin_color_scheme)) {
                    choice = rec.viin_color_scheme;
                }
            } catch {
                // Degrade to the boot-stamped effective; the UI stays whatever the server painted.
            }
            state.scheme = choice;
            applyEffective(choice);
            if (choice === "auto") {
                startOsListener();
            } else {
                stopOsListener();
            }
        })();

        // Re-assert density from the cookie (idempotent with the server boot stamp).
        applyDensity(density);

        return {
            state,
            // Current getters (TDD: the service exposes current scheme/density).
            get scheme() {
                return state.scheme;
            },
            get density() {
                return state.density;
            },
            /** Set the color-scheme CHOICE (light|dark|auto): PERSIST (pref + effective cookie) and
             *  RELOAD. Dark mode is a RECOMPILED server bundle (web.assets_web_dark), which a
             *  server-selected bundle cannot swap into without a reload - so the toggle does NOT
             *  instant-flip [data-bs-theme]; it persists and reloads, after which the base
             *  ir.http.color_scheme reads the cookie, serves the dark bundle, and boot-stamps the
             *  paint. */
            async setScheme(choice) {
                if (!SCHEMES.includes(choice)) {
                    return;
                }
                state.scheme = choice;
                // Persist the EFFECTIVE (light|dark) scheme to the cookie the server reads on the
                // next render. NO instant dataset.bsTheme flip (the recompiled bundle carries dark).
                cookie.set(SCHEME_COOKIE, resolveEffective(choice));
                if (choice === "auto") {
                    startOsListener();
                } else {
                    stopOsListener();
                }
                // Persist the CHOICE (SELF_WRITEABLE -> a plain internal user may set their own),
                // then reload so the server serves the correct bundle. AWAIT the write so it lands
                // before the reload unloads the page (the fresh-session boot then reads the stored
                // preference); best-effort so a restricted session's failed write never blocks the
                // reload - the cookie already carries the effective scheme for the imminent render.
                try {
                    await orm.write("res.users", [user.userId], { viin_color_scheme: choice });
                } catch {
                    // ignore: the effective cookie is already set for the reload below.
                }
                browser.location.reload();
            },
            /** Set the density CHOICE (comfortable|compact): apply instantly + persist the cookie. */
            setDensity(value) {
                if (!DENSITIES.includes(value)) {
                    return;
                }
                state.density = value;
                applyDensity(value);
            },
        };
    },
};

registry.category("services").add("viin_theme", viinThemeService);
