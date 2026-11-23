import { animationFrame, describe, expect, mockMatchMedia, test } from "@odoo/hoot";
import {
    defineModels,
    fields,
    getService,
    makeTestApp,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";
import { cookie } from "@web/core/browser/cookie";
import { location } from "@web/core/browser/browser";
import { ViinThemePlugin } from "@viin_backend_theme/webclient/viin_theme_plugin";

// Behaviour guards for the `ViinThemePlugin` (observable state, not internals). Dark mode is a
// recompiled server bundle (web.assets_web_dark) that cannot swap without a reload, so
// setScheme(choice) must
//   (a) persist the choice to res.users.viin_color_scheme (ORM write),
//   (b) persist the effective (light|dark) scheme to the `color_scheme` cookie the server reads, and
//   (c) reload via location.reload() so the server serves the dark bundle and boot-stamps
//       the paint, without any instant [data-bs-theme] flip.
// Density is attribute-scoped SCSS, not a server bundle: setDensity must stamp data-viin-density and
// persist its cookie without reloading.

describe("ViinThemePlugin (persist + reload)", () => {
    // The theme depends on viin_brand_mail, so its production JS boots the mail/discuss service
    // graph in makeTestApp. Spread the full mail mock model set so those boot RPCs resolve, and
    // override res.users with the per-user field so the boot read and the persist write resolve.
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

    /** Start the test app (which eagerly starts the plugin) and let its async boot reconcile settle,
     *  so the subsequent explicit setScheme/setDensity call is the last writer (no boot race). */
    async function startPlugin() {
        await makeTestApp();
        await animationFrame();
        return getService(ViinThemePlugin);
    }

    test("setScheme('dark') persists the pref + effective cookie and reloads, with no instant paint flip", async () => {
        let writtenVals = null;
        onRpc("res.users", "write", ({ args }) => {
            writtenVals = args[1];
            return true;
        });
        patchWithCleanup(location, { reload: () => expect.step("reload") });

        const plugin = await startPlugin();
        const paintBefore = root.dataset.bsTheme; // boot-stamped effective (default light)

        plugin.setScheme("dark");
        await animationFrame(); // flush the fire-and-forget ORM write

        expect.verifySteps(["reload"], {
            message:
                "setScheme('dark') must call location.reload() so the server serves the " +
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
        patchWithCleanup(location, { reload: () => expect.step("reload") });

        const plugin = await startPlugin();
        plugin.setScheme("auto");
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
        // Density is attribute-scoped SCSS (no server bundle), so the scheme reload must not bleed
        // onto it: it stays an instant, reload-free flip.
        patchWithCleanup(location, { reload: () => expect.step("reload") });

        const plugin = await startPlugin();
        plugin.setDensity("compact");
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
