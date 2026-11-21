/** @odoo-module **/

// viin_theme service: the single source that resolves and persists the backend appearance (color
// scheme and density). The scheme toggle persists and reloads, because dark is a recompiled server
// bundle; density is an instant, reload-free attribute flip.
//
//  - Scheme CHOICE (light/dark/auto) is the user preference res.users.viin_color_scheme
//    (self-writeable), the source of truth for the radio state. It is not known synchronously at
//    boot, so it is reconciled with one lightweight self-read.
//  - EFFECTIVE scheme (light/dark) is what the server serves; 'auto' resolves to the OS preference
//    via matchMedia("(prefers-color-scheme: dark)").
//  - setScheme persists the effective scheme to the `color_scheme` cookie the server reads
//    (ir.http.color_scheme, boot reflection) and the choice to the user field, then reloads: a
//    server-selected bundle cannot swap without a reload. It does not flip [data-bs-theme]; the
//    boot stamp is only a hint for Bootstrap dark component variants.
//  - Density CHOICE (comfortable/compact) has no server field: the `viin_density` cookie is the
//    source of truth (the server stamps data-viin-density from it, FOUC-free). Applying it sets
//    documentElement.dataset.viinDensity instantly; density.scss carries the size rules.

import { registry } from "@web/core/registry";
import { cookie } from "@web/core/browser/cookie";
import { browser } from "@web/core/browser/browser";
import { user } from "@web/core/user";
import { reactive } from "@odoo/owl";

// The server reads these cookie names (ir.http.color_scheme and the boot reflection): do not rename.
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
            get scheme() {
                return state.scheme;
            },
            get density() {
                return state.density;
            },
            /** Set the color-scheme CHOICE (light|dark|auto): persist the preference and the effective
             *  cookie, then reload so the server serves the matching bundle (no [data-bs-theme] flip). */
            async setScheme(choice) {
                if (!SCHEMES.includes(choice)) {
                    return;
                }
                state.scheme = choice;
                // The server reads the effective scheme from the cookie on the next render.
                cookie.set(SCHEME_COOKIE, resolveEffective(choice));
                if (choice === "auto") {
                    startOsListener();
                } else {
                    stopOsListener();
                }
                // Await the write so it lands before the reload unloads the page; best-effort, so a
                // restricted session's failed write never blocks the reload (the cookie already
                // carries the effective scheme).
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
