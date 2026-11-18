/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { titleService } from "@web/core/browser/title_service";

// De-brand core's empty-state title fallback (`Object.values(titleParts).join(" - ") || "Odoo"`)
// instead of keeping a permanent title part: a permanent part would be joined into every composed
// title ("Viindoo - <action title>").
//
// The private `titleParts` closure has no hook, so the two public entry points (`setParts` and
// `setCounters`) are wrapped; once core has recomputed `document.title`, the "Odoo" fallback is
// rewritten to "Viindoo" only when `getParts()` is empty, so a composed title is never touched.
// A bare backend boot is already branded by the `webclient_bootstrap` template, which sets the
// title server-side.
const ODOO_WORDMARK = "Odoo";
const VIINDOO_WORDMARK = "Viindoo";

/**
 * After delegating to core's real `setParts`/`setCounters` (which already recomputed
 * `document.title`), rewrite the empty-composition fallback from "Odoo" to "Viindoo" - and ONLY
 * the fallback: `getParts()` returning zero keys is exactly core's own precondition for reaching
 * the `|| "Odoo"` branch, so a composed title is never touched.
 * @param {{ getParts: () => Record<string, string> }} titleApi
 */
function debrandEmptyFallback(titleApi) {
    if (Object.keys(titleApi.getParts()).length !== 0) {
        return;
    }
    if (document.title.includes(ODOO_WORDMARK)) {
        // Literal substitution, not an assignment: counters already prepend "(N) " to the fallback.
        document.title = document.title.replace(ODOO_WORDMARK, VIINDOO_WORDMARK);
    } else if (document.title !== VIINDOO_WORDMARK && !document.title.includes(VIINDOO_WORDMARK)) {
        // console.warn, not console.error: this wrapper runs on every setParts/setCounters call in
        // every suite that loads web.assets_backend, and a console.error would fail suites this
        // module does not own. The guard skips a title that is already "Viindoo".
        console.warn(
            "viin_brand: the title service's empty-composition fallback was NOT " +
                'de-branded. Expected document.title to contain "Odoo" (Odoo 19.0 core\'s own ' +
                "empty-state fallback, web/static/src/core/browser/title_service.js:38), but " +
                `found "${document.title}". Either core changed the fallback (make this patch ` +
                "handle the new shape) or another module already rewrote it. Review " +
                "viin_brand/static/src/core/browser/title_service.js against current core."
        );
    }
}

patch(titleService, {
    start() {
        const titleApi = super.start(...arguments);
        const setParts = titleApi.setParts;
        const setCounters = titleApi.setCounters;
        titleApi.setParts = (parts) => {
            setParts(parts);
            debrandEmptyFallback(titleApi);
        };
        titleApi.setCounters = (counters) => {
            setCounters(counters);
            debrandEmptyFallback(titleApi);
        };
        return titleApi;
    },
});
