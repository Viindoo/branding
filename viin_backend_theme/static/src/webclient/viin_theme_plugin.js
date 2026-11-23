// ViinThemePlugin: the single source that resolves and persists the backend appearance (color
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

import { Plugin, signal, usePlugin } from "@odoo/owl";
import { cookie } from "@web/core/browser/cookie";
import { browser, location } from "@web/core/browser/browser";
import { ORM } from "@web/core/orm_plugin";
import { services } from "@web/core/services";
import { user } from "@web/core/user";

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

export class ViinThemePlugin extends Plugin {
    orm = usePlugin(ORM);

    // Seeded provisionally from the boot-stamped effective scheme; the true CHOICE (which may be
    // 'auto') is reconciled by the self-read in setup() and updates `scheme`.
    bootEffective = document.documentElement.dataset.bsTheme === "dark" ? "dark" : "light";
    scheme = signal(this.bootEffective);
    // Read from the FOUC-free cookie the server already stamped; default comfortable.
    density = signal(
        DENSITIES.includes(cookie.get(DENSITY_COOKIE)) ? cookie.get(DENSITY_COOKIE) : "comfortable"
    );

    // matchMedia listener lifecycle - active ONLY while the choice is 'auto'.
    mql = null;
    onOsChange = () => this.applyEffective("auto");

    setup() {
        // Re-assert density from the cookie (idempotent with the server boot stamp).
        this.applyDensity(this.density());
        this.reconcileScheme();
    }

    /**
     * Reconcile the true CHOICE from the stored preference (self-readable). Non-blocking: the boot
     * paint is already correct for explicit light/dark. At boot the server cannot resolve 'auto'
     * (ir.http.color_scheme falls back to light), so once the choice is known to be 'auto' it is
     * resolved via matchMedia, re-applied, and OS changes are tracked.
     */
    async reconcileScheme() {
        let choice = this.bootEffective;
        try {
            const [rec] = await this.orm.read("res.users", [user.userId], ["viin_color_scheme"]);
            if (rec && SCHEMES.includes(rec.viin_color_scheme)) {
                choice = rec.viin_color_scheme;
            }
        } catch {
            // Degrade to the boot-stamped effective; the UI stays whatever the server painted.
        }
        this.scheme.set(choice);
        this.applyEffective(choice);
        this.trackOsPreference(choice === "auto");
    }

    startOsListener() {
        if (!this.mql) {
            this.mql = browser.matchMedia(DARK_MEDIA);
            this.mql.addEventListener("change", this.onOsChange);
        }
    }

    stopOsListener() {
        if (this.mql) {
            this.mql.removeEventListener("change", this.onOsChange);
            this.mql = null;
        }
    }

    trackOsPreference(isAuto) {
        if (isAuto) {
            this.startOsListener();
        } else {
            this.stopOsListener();
        }
    }

    /** Flip the paint instantly and keep the cookie in sync so a reload and core cookie-widgets agree. */
    applyEffective(choice) {
        const effective = resolveEffective(choice);
        document.documentElement.dataset.bsTheme = effective;
        cookie.set(SCHEME_COOKIE, effective);
    }

    applyDensity(value) {
        document.documentElement.dataset.viinDensity = value;
        cookie.set(DENSITY_COOKIE, value);
    }

    /**
     * Set the color-scheme CHOICE (light|dark|auto): persist the preference and the effective
     * cookie, then reload so the server serves the matching bundle (no [data-bs-theme] flip).
     */
    async setScheme(choice) {
        if (!SCHEMES.includes(choice)) {
            return;
        }
        this.scheme.set(choice);
        // The server reads the effective scheme from the cookie on the next render.
        cookie.set(SCHEME_COOKIE, resolveEffective(choice));
        this.trackOsPreference(choice === "auto");
        // Await the write so it lands before the reload unloads the page; best-effort, so a
        // restricted session's failed write never blocks the reload (the cookie already carries
        // the effective scheme).
        try {
            await this.orm.write("res.users", [user.userId], { viin_color_scheme: choice });
        } catch {
            // ignore: the effective cookie is already set for the reload below.
        }
        location.reload();
    }

    /** Set the density CHOICE (comfortable|compact): apply instantly + persist the cookie. */
    setDensity(value) {
        if (!DENSITIES.includes(value)) {
            return;
        }
        this.density.set(value);
        this.applyDensity(value);
    }
}

services.add(ViinThemePlugin);
