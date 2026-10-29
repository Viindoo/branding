/** @odoo-module **/

import { describe, expect, test } from "@odoo/hoot";

import { titleService } from "@web/core/browser/title_service";

describe.current.tags("headless");

// Core's title service composes `document.title` from a `titleParts` map:
//     const name = Object.values(titleParts).join(" - ") || "Odoo";
// viin_brand_web de-brands ONLY that empty-state fallback: when no part is composed,
// document.title reads "Viindoo", never core's stock "Odoo". The brand must never become a
// permanent joined part: when a real part is composed (the shape core's action service uses,
// `env.services.title.setParts({ action: controller.displayName })`), document.title equals that
// part alone. A permanent "Viindoo" part would turn every later title into
// "Viindoo - <action title>" and break exact-match title lookups such as the website event
// pages SEO tour.
//
// The fix module is loaded eagerly through this module's `web.assets_backend` bundle, so
// importing core's `titleService` is enough to observe the patched behaviour.
//
// `titleService.start()` returns a fresh API object with its own closure-local state per call;
// each test calls it again so tests stay independent of execution order. `setParts({})` forces
// a recompute of the current, possibly still empty, state.

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
