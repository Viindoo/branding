/** @odoo-module **/

import { describe, expect, test } from "@odoo/hoot";

import { titleService } from "@web/core/browser/title_service";

describe.current.tags("headless");

// Business rule under protection (findings.md item 5 in this run's debug log + decisions.md
// "Decided without a gate" #5): core's title service composes `document.title` from a
// `titleParts` map:
//     const name = Object.values(titleParts).join(" - ") || "Odoo";
//   (web/static/src/core/browser/title_service.js:38, 19.0)
// viin_brand_web must de-brand ONLY that EMPTY-STATE FALLBACK - when no part is composed,
// document.title must read "Viindoo", never core's stock "Odoo". That de-brand must NEVER become
// a permanent joined PART: when a real part IS composed (the exact shape core's own
// action_service.js uses - `env.services.title.setParts({ action: controller.displayName })`,
// action_service.js:900, and website_builder_action.js:361-363 for the website builder's outer
// title), `document.title` must equal that part ALONE.
//
// This is the regression pin for a real production defect: viin_brand_web/static/src/webclient/
// webclient.js used to patch `WebClient.prototype.setup()` to call
// `this.title.setParts({ zopenerp: "Viindoo" })` once at boot and never clear it - so
// `titleParts` carried a permanent "Viindoo" entry alongside every later action's own title part,
// and `Object.values(titleParts).join(" - ")` corrupted EVERY composed title afterwards into
// "Viindoo - <action title>". Caught by production tour
// `website_event.tests.test_website_event.TestUi.test_website_event_pages_seo` step [8/8]:
// trigger `head:has(title:text(Hello, world!)):not(:visible)` - `:text()` is an EXACT match, not
// `:contains()` - which failed because the outer `document.title` was
// "Viindoo - Hello, world!" instead of the expected "Hello, world!".
//
// RED today, confirmed by reading source (no live instance this session): as of this test,
// `title_service.js` itself is UNPATCHED by viin_brand_web - the only existing de-brand patch
// touches `WebClient.prototype.setup()`, a different object entirely (and is being relocated by
// this work-item to stop the leak described above). Calling `titleService.start()` fresh below
// therefore returns core's STOCK closure: with `titleParts` empty, `updateTitle()` computes
// `name = "" || "Odoo"`, so `document.title === "Odoo"` - the first test's
// `expect(document.title).toBe("Viindoo")` fails today for exactly that reason. Once the fix is
// wired into this module's `web.assets_backend` manifest bundle (an eager entry, same convention
// as this module's existing `core/colors/colors.js` / `core/errors/error_dialogs.js`), Hoot's
// `ModuleSetLoader.setup()` runs it before this test module's body executes - see
// `user_menu_debrand.test.js` / `upgrade_dialog_debrand.test.js` headers for the same mechanism -
// so no side-effect import of the fix module is needed here; importing core's `titleService`
// directly is enough to observe the patched behaviour once it exists.
//
// `titleService.start()` takes no meaningful parameters and returns a FRESH API object with its
// own closure-local `titleParts`/`titleCounters` state per call - each test below calls it again
// rather than sharing one instance, so tests stay independent of execution order (FIRST rule).
// `setParts()`/`setCounters()` always call the internal `updateTitle()` after their loop, even
// for an empty object, so `setParts({})` is a deterministic way to force a recompute of the
// current (possibly still-empty) state without depending on a prior call having happened.

test("empty title composition falls back to the Viindoo brand, never Odoo", () => {
    const title = titleService.start();
    title.setParts({});
    expect(document.title).toBe("Viindoo");
    expect(document.title).not.toBe("Odoo");
});

test("a composed title (e.g. an action) is never joined with the Viindoo de-brand", () => {
    const title = titleService.start();
    title.setParts({ action: "Hello, world!" });
    // Exact match, mirroring the production tour's `title:text(Hello, world!)` assertion - not a
    // substring check, so a "Viindoo - Hello, world!" leak would fail this the same way it fails
    // the tour.
    expect(document.title).toBe("Hello, world!");
    expect(document.title).not.toInclude("Viindoo");
});

test("clearing the last composed part reverts the title to the Viindoo fallback", () => {
    const title = titleService.start();
    title.setParts({ action: "Hello, world!" });
    expect(document.title).toBe("Hello, world!");
    // A falsy value deletes the key (core's own contract: `if (!val) delete titleParts[key]`),
    // so titleParts is empty again here - proves the de-brand fallback is LIVE, not a one-time
    // value stamped only at boot.
    title.setParts({ action: null });
    expect(document.title).toBe("Viindoo");
});

test("the counter prefix on an empty composition still reads the Viindoo brand", () => {
    const title = titleService.start();
    title.setCounters({ chat: 3 });
    expect(document.title).toBe("(3) Viindoo");
    expect(document.title).not.toBe("(3) Odoo");
});
