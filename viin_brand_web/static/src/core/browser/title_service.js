/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { titleService } from "@web/core/browser/title_service";

// De-brand the title service's own EMPTY-STATE fallback, instead of injecting a permanent title
// PART (owner decision, branding core-test regressions run 2026-08-17, decisions.md "Decided
// without a gate" #5). Core composes `document.title` from a `titleParts` map:
//     const name = Object.values(titleParts).join(" - ") || "Odoo";
//   -> web/static/src/core/browser/title_service.js:38 (19.0)
// - only reaching the `|| "Odoo"` literal when NO part is currently set.
//
// Relocated FROM viin_brand_web/static/src/webclient/webclient.js, which used to patch
// `WebClient.prototype.setup()` to call `this.title.setParts({ zopenerp: "Viindoo" })` once at
// boot and never clear it. That made `titleParts` carry a PERMANENT "Viindoo" entry, so
// `Object.values(titleParts).join(" - ")` joined it into every later composed title
// ("Viindoo - <action title>" instead of just "<action title>") - caught by production tour
// `website_event.tests.test_website_event.TestUi.test_website_event_pages_seo` step [8/8], whose
// `title:text(Hello, world!)` trigger is an EXACT match. This patch fixes the MECHANISM, not just
// the symptom: it touches the SAME fallback site core itself designates (`|| "Odoo"`), so the
// brand shows exactly where core would otherwise show its own name, and nowhere else.
//
// `titleService` is a plain object (not a class prototype) exporting a `start()` factory;
// `patch()` supports plain objects the same way it supports class prototypes (see
// web/static/src/core/utils/patch.js - the patch description/skeleton mechanism is generic over
// any object). We do NOT reimplement `updateTitle()` - its `titleParts`/`titleCounters` state is a
// private closure with no exposed hook - so instead we wrap the two PUBLIC entry points that
// trigger it (`setParts`/`setCounters`) and, only when the underlying composition is now empty,
// rewrite the "Odoo" fallback core just wrote into `document.title` to "Viindoo". This never fires
// while any part is set: `getParts()` is checked AFTER delegating to the real implementation, so a
// composed title (e.g. an `action` part - web/static/src/webclient/actions/action_service.js:900,
// or website/static/src/client_actions/website_preview/website_builder_action.js:361-363) is left
// completely untouched.
//
// No proactive call is added at `start()`/boot: a bare backend boot with no action loaded is
// ALREADY branded correctly by a separate, pre-existing, unrelated mechanism -
// viin_brand_web/views/webclient_template.xml's `webclient_bootstrap` template sets
// `<t t-set="title">Viindoo</t>` SERVER-SIDE, rendered before any JS runs
// (web.layout's `<title t-esc="title or 'Odoo'"/>`,
// odoo/addons/web/views/webclient_templates.xml:22). Writing here too would be redundant with,
// never a substitute for, that SSR value.
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
        // Literal substitution, not an outright assignment: keeps working unmodified if core ever
        // qualifies the fallback (e.g. counters already prepend "(N) "), same rationale as this
        // module's core/dialog/dialog.js.
        document.title = document.title.replace(ODOO_WORDMARK, VIINDOO_WORDMARK);
    } else if (document.title !== VIINDOO_WORDMARK && !document.title.includes(VIINDOO_WORDMARK)) {
        // console.warn, deliberately NOT console.error: this module's other de-brand guards
        // (core/dialog/dialog.js, core/errors/error_dialogs.js) check a precondition exactly ONCE,
        // at a call site only THEIR OWN test mounts. This wrapper instead runs on EVERY real
        // setParts/setCounters call across the whole app, AND across the whole
        // `web.assets_unit_tests` HOOT bundle (web.assets_unit_tests_setup includes
        // web.assets_backend, so this eager patch loads into every HOOT run, not just this
        // module's own suites). A console.error becomes a ChromeBrowserException that fails
        // whichever suite happens to be running at the time (odoo/tests/common.py:1732) - too
        // broad a blast radius for a diagnostic that guards against a future wording change in
        // core, not a functional defect: it must never be able to fail a suite this module does
        // not own. console.warn is only logged, never fatal (common.py:1817 _TO_LEVEL), so a
        // genuine future drift stays visible to a developer without risking an unrelated green
        // suite. Guarded against re-firing when the title is already "Viindoo" (e.g. the SSR boot
        // value untouched by this call).
        console.warn(
            "viin_brand_web: the title service's empty-composition fallback was NOT " +
                'de-branded. Expected document.title to contain "Odoo" (Odoo 19.0 core\'s own ' +
                "empty-state fallback, web/static/src/core/browser/title_service.js:38), but " +
                `found "${document.title}". Either core changed the fallback (make this patch ` +
                "handle the new shape) or another module already rewrote it. Review " +
                "viin_brand_web/static/src/core/browser/title_service.js against current core."
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
