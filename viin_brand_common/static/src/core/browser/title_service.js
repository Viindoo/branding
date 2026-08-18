/** @odoo-module **/
/* Copyright 2026 Viindoo
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { titleService } from "@web/core/browser/title_service";

// Viindoo tab-title rule: brand the tab title's EMPTY-CASE FALLBACK, never inject a permanent
// title part. Core composes the title as
// `Object.values(titleParts).join(" - ") || "Odoo"` (web/static/src/core/browser/title_service.js)
// - core itself never sets a part, so "Odoo" is ONLY ever the empty-case fallback and never
// appears beside a real title. The previous patch here (webclient.js, now removed) called
// `this.title.setParts({ zopenerp: "Viindoo" })` once at WebClient setup, which added a
// PERMANENT entry to titleParts - so every later real title got "Viindoo - " prepended to it
// (e.g. the website SEO dialog's "Hello, world!" became "Viindoo - Hello, world!").
//
// `updateTitle()` and its `|| "Odoo"` fallback live inside core's `start()` closure and are not
// reachable from outside; the service's only public surface is
// `{ current, getParts, setCounters, setParts }`. This patch composes with that surface instead
// of re-implementing updateTitle(): it always lets core compute the title exactly as it always
// does, then - only when core's own `getParts()` proves titleParts is empty (the fallback just
// fired) - replaces the trailing "Odoo" core just wrote into document.title with "Viindoo". A
// title with any real part set is never touched, because getParts() will not be empty for it.
//
// Gated on the server-stamped session.viin_brand marker (see viin_brand_common's ir_http
// session_info()) so core's own QUnit/Hoot suites, whose mock sessions lack the marker, keep
// asserting the plain "Odoo" title - the guard was added by branding commit f35f41c to fix
// exactly that regression (runbot 223235/396399); do not remove it.
patch(titleService, {
    start(env, dependencies) {
        const originalTitleService = super.start(env, dependencies);
        if (!session.viin_brand) {
            return originalTitleService;
        }

        function brandEmptyFallback() {
            if (Object.keys(originalTitleService.getParts()).length === 0) {
                document.title = document.title.replace(/Odoo$/, "Viindoo");
            }
        }

        const brandedTitleService = {
            get current() {
                return originalTitleService.current;
            },
            getParts: originalTitleService.getParts,
            setParts(parts) {
                originalTitleService.setParts(parts);
                brandEmptyFallback();
            },
            setCounters(counters) {
                originalTitleService.setCounters(counters);
                brandEmptyFallback();
            },
        };
        // Nothing may ever call setParts/setCounters at all (e.g. a bare WebClient mount with no
        // action loaded yet) - force the branded empty state once right here too, through the
        // wrapped setParts so the same brandEmptyFallback() path applies.
        brandedTitleService.setParts({});

        return brandedTitleService;
    },
});
