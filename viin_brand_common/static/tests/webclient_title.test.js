/** @odoo-module **/
/* Copyright 2026 Viindoo
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { expect, test } from "@odoo/hoot";
import { getService, mountWithCleanup, patchWithCleanup } from "@web/../tests/web_test_helpers";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";

// Protects the Viindoo tab-title rule against BOTH failure directions at once. Core composes the
// tab title as `Object.values(titleParts).join(" - ") || "Odoo"` (title_service.js:38) - core
// itself never sets a part, so "Odoo" is only ever the empty-case fallback and never appears
// beside a real title.
//
//   1. Empty case is branded  - with no title part set, the tab reads "Viindoo", not "Odoo".
//   2. Non-empty case is untouched - with a part set, the tab reads exactly what core composed,
//      nothing prepended.
//
// Either half alone is satisfiable by a wrong implementation, so both are asserted together: an
// implementation that deletes the branding outright satisfies half 2 while breaking half 1; the
// permanent-part patch this suite was written against (webclient.js) satisfies half 1 by accident
// while breaking half 2 - any real title part gets "Viindoo - " prepended to it.
//
// Both tests patch session.viin_brand themselves. That flag is the server-stamped marker the
// patch gates on (see viin_brand_common/models/ir_http.py session_info()) so that core's own
// ActionManager suites, whose mock sessions lack the marker, keep asserting the plain "Odoo"
// title - Hoot's mock session here lacks it by default too, so a test that left it unset would
// never exercise the branded path at all.

test("with no title part set, the tab title reads the Viindoo brand, not the Odoo fallback", async () => {
    patchWithCleanup(session, { viin_brand: true });

    await mountWithCleanup(WebClient);

    expect(getService("title").current).toBe("Viindoo");
});

test("with a title part set, the tab title reads exactly that part, with nothing prepended", async () => {
    patchWithCleanup(session, { viin_brand: true });

    await mountWithCleanup(WebClient);
    // Simulates what any real screen does once mounted (e.g. an action naming itself in the tab) -
    // the observable outcome the rule protects, never the internal titleParts object.
    getService("title").setParts({ action: "Hello, world!" });

    expect(getService("title").current).toBe("Hello, world!");
});
