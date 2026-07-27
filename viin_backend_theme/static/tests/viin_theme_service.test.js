import { animationFrame, describe, expect, mockMatchMedia, test } from "@odoo/hoot";
import {
    defineModels,
    fields,
    getService,
    makeMockEnv,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";
import { cookie } from "@web/core/browser/cookie";
import { browser } from "@web/core/browser/browser";

// T-1 (PR #658 review-fix) - behavior guards for the `viin_theme` service under Option A.
//
// WHAT CHANGED, AND WHAT IS PROTECTED (observable state, not internals). Dark mode is now a
// RECOMPILED server bundle (web.assets_web_dark), and a server-selected bundle cannot swap without a
// reload. So the SCHEME toggle no longer instant-flips [data-bs-theme]: setScheme(choice) must
//   (a) PERSIST the choice to res.users.viin_color_scheme (ORM write),
//   (b) PERSIST the EFFECTIVE (light|dark) scheme to the `color_scheme` cookie the server reads, and
//   (c) RELOAD via browser.location.reload() so the server serves the dark bundle + boot-stamps the
//       paint - WITHOUT any instant [data-bs-theme] flip in the toggle path.
// DENSITY stays instant (it is attribute-scoped SCSS, not a server bundle): setDensity must stamp
// data-viin-density and persist its cookie WITHOUT reloading.
//
// Each test removes/would-remove exactly one guarantee to prove RED-on-behavior-removal:
//   drop reload -> the verifySteps(["reload"]) fails; instant-flip the paint -> the "paint unchanged"
//   assertion fails; drop the ORM write / cookie -> the persist assertions fail; make density reload
//   -> the density verifySteps([]) fails.
//
// GROUNDED (OSM 19.0 + core source): service-test shape from
// web/static/tests/webclient/reload_company_service.test.js (makeMockEnv + getService +
// defineModels); browser.location mocked via patchWithCleanup(browser.location, { reload })
// (web/static/tests/core/debug/debug_manager.test.js:206); cookie + matchMedia test-isolated
// (@odoo/hoot mock window). This ADAPTS the retired instant-apply guards: the old "flips the html
// root to dark" / "live OS re-paint on toggle" assertions snapshotted the no-reload architecture
// C-2 removed, so they are dropped rather than translated.

describe("viin_theme service (persist + reload)", () => {
    // The theme depends on viin_brand_mail, so its production JS (in web.assets_backend, included by
    // the unit-test setup bundle) boots the mail/discuss service graph in makeMockEnv. Spread the
    // full mail mock model set so those boot RPCs resolve, and OVERRIDE res.users with the per-user
    // field so the service's boot reconcile read + its persist write resolve cleanly.
    class ResUsers extends mailModels.ResUsers {
        viin_color_scheme = fields.Selection({
            selection: [
                ["light", "Light"],
                ["dark", "Dark"],
                ["auto", "System"],
            ],
            default: "light",
        });
    }
    defineModels({ ...mailModels, ResUsers });

    const root = document.documentElement;

    /** Start the mock env (which eagerly starts the service) and let its async boot reconcile settle,
     *  so the subsequent explicit setScheme/setDensity call is the last writer (no boot race). */
    async function startService() {
        await makeMockEnv();
        await animationFrame();
        return getService("viin_theme");
    }

    test("setScheme('dark') persists the pref + effective cookie and reloads, with no instant paint flip", async () => {
        let writtenVals = null;
        onRpc("res.users", "write", ({ args }) => {
            writtenVals = args[1];
            return true;
        });
        patchWithCleanup(browser.location, { reload: () => expect.step("reload") });

        const service = await startService();
        const paintBefore = root.dataset.bsTheme; // boot-stamped effective (default light)

        service.setScheme("dark");
        await animationFrame(); // flush the fire-and-forget ORM write

        expect.verifySteps(["reload"], {
            message:
                "setScheme('dark') must call browser.location.reload() so the server serves the " +
                "recompiled web.assets_web_dark bundle (a server-selected bundle cannot swap without a reload).",
        });
        expect(cookie.get("color_scheme")).toBe("dark", {
            message:
                "setScheme('dark') must persist the EFFECTIVE scheme to the color_scheme cookie the server reads.",
        });
        expect(writtenVals).toEqual(
            { viin_color_scheme: "dark" },
            { message: "setScheme('dark') must persist the CHOICE to res.users.viin_color_scheme." }
        );
        expect(root.dataset.bsTheme).toBe(paintBefore, {
            message:
                "the toggle must NOT instant-flip [data-bs-theme]; the recompiled bundle applies dark " +
                "after the reload, not synchronously in the toggle path.",
        });
    });

    test("setScheme('auto') persists the OS-EFFECTIVE scheme to the cookie (not the raw choice) and reloads", async () => {
        // The cookie stores the EFFECTIVE light|dark the server serves; 'auto' is the only case where
        // choice != effective, so it is what proves "effective, not raw choice" is written.
        mockMatchMedia({ "prefers-color-scheme": "dark" });
        let writtenVals = null;
        onRpc("res.users", "write", ({ args }) => {
            writtenVals = args[1];
            return true;
        });
        patchWithCleanup(browser.location, { reload: () => expect.step("reload") });

        const service = await startService();
        service.setScheme("auto");
        await animationFrame();

        expect.verifySteps(["reload"], {
            message:
                "setScheme('auto') must reload so the server re-resolves and serves the correct bundle.",
        });
        expect(cookie.get("color_scheme")).toBe("dark", {
            message:
                "'auto' with a dark OS preference must persist the EFFECTIVE scheme 'dark' to the " +
                "color_scheme cookie (matchMedia-resolved), never the literal 'auto'.",
        });
        expect(writtenVals).toEqual(
            { viin_color_scheme: "auto" },
            {
                message:
                    "the stored PREFERENCE stays the raw 'auto' choice (only the cookie is effective).",
            }
        );
    });

    test("setDensity('compact') applies instantly and does NOT reload", async () => {
        // Non-regression guard: density is theme-owned attribute-scoped SCSS (no server bundle), so
        // T-1's reload must NOT bleed onto density - it stays an instant, reload-free flip.
        patchWithCleanup(browser.location, { reload: () => expect.step("reload") });

        const service = await startService();
        service.setDensity("compact");
        await animationFrame();

        expect(root.dataset.viinDensity).toBe("compact", {
            message:
                "setDensity('compact') must stamp data-viin-density=compact on <html> instantly.",
        });
        expect(cookie.get("viin_density")).toBe("compact", {
            message: "setDensity('compact') must persist the choice to the viin_density cookie.",
        });
        expect.verifySteps([], {
            message:
                "density is attribute-scoped SCSS, not a server bundle - it must NOT trigger a page reload.",
        });
    });
});
