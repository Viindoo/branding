/** @odoo-module **/
/* Copyright 2026 Viindoo
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { expect, test } from "@odoo/hoot";
import { mockService, mountWithCleanup, patchWithCleanup } from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";

// Re-implementation of the QUnit suite retired at 18.0 (webclient_tests.esm.js). Core's
// WebClient._loadDefaultApp is byte-identical 17.0 -> 18.0 (odoo_17.0 webclient.js:87-94 vs
// odoo_18.0 webclient.js:142-149), but web_responsive's patch of it
// (static/src/components/webclient/webclient.js) was rewritten between the two series: it no
// longer checks the actions registry, it reads session.apps_menu?.is_redirect_home instead. These
// four tests protect the guard's actual 18.0 shape, not its old 17.0 mechanism.
//
// The fourth test is load-bearing beyond this file: forward-port commit 221946b (a registry-
// existence guard against core mail's stripped-down multi-tab QUnit env throwing
// "Cannot find apps_menu in this registry!") was classified "already-satisfied at 18.0" on the
// strength of THIS guard existing under its new session-flag shape - see
// forward-port/17-to-18-20260807/web_responsive/intents/221946b.md. If this test cannot fail for
// the right reason, that classification has nothing behind it.

// web_responsive depends on `mail`, which patches the WebClient's NavBar/systray with components
// that reach for mail's own server models. Without mail's mock models registered, mounting the
// WebClient aborts with `Cannot find a definition for model "discuss.channel"` and all four tests
// below fail for a harness reason rather than the guard they exist to protect. Module-level call,
// matching core's own convention.
defineMailModels();

/**
 * A minimal, spy-able stand-in for the core "menu" service (@web/webclient/menus/menu_service).
 * Recording selectMenu() is exactly "the stock post-login destination ran" - the only observable
 * side effect of core's real WebClient._loadDefaultApp().
 */
function mockMenuService() {
    mockService("menu", () => ({
        getMenu: (menuId) => (menuId === "root" ? { children: [1] } : { id: 1, appID: 1 }),
        getAll: () => [{ id: 1, appID: 1 }],
        getApps: () => [{ id: 1, appID: 1 }],
        getCurrentApp: () => undefined,
        setCurrentMenu: () => {},
        reload: () => {},
        selectMenu(menu) {
            const menuId = typeof menu === "number" ? menu : menu.id;
            expect.step(`selectMenu:${menuId}`);
        },
    }));
}

/**
 * A minimal, spy-able stand-in for web_responsive's real "apps_menu" service
 * (static/src/components/apps_menu/apps_menu_service.js). Recording toggleMenu() is exactly
 * "the Apps menu was opened instead of the stock destination".
 */
function mockAppsMenuService() {
    mockService("apps_menu", () => ({
        toggleMenu(openState) {
            expect.step(`toggleMenu:${openState}`);
        },
    }));
}

test(
    "apps_menu preference enabled on the session -> WebClient boots into the Apps menu instead " +
        "of the stock destination",
    async () => {
        mockMenuService();
        mockAppsMenuService();
        patchWithCleanup(session, { apps_menu: { is_redirect_home: true } });

        await mountWithCleanup(WebClient);

        await expect.waitForSteps(["toggleMenu:true"]);
    }
);

test(
    "apps_menu preference disabled on the session -> WebClient boots into Odoo's standard " +
        "post-login destination",
    async () => {
        mockMenuService();
        mockAppsMenuService();
        patchWithCleanup(session, { apps_menu: { is_redirect_home: false } });

        await mountWithCleanup(WebClient);

        // Guards against shipping the preference with an inverted direction: the stock
        // default-app selection must run and the Apps menu must never open.
        await expect.waitForSteps(["selectMenu:1"]);
    }
);

test(
    "no apps_menu preference on the session at all -> WebClient still boots into the standard " +
        "destination without throwing",
    async () => {
        mockMenuService();
        mockAppsMenuService();
        // Deliberately do not patch session.apps_menu: session.apps_menu?.is_redirect_home must
        // resolve to undefined (falsy) rather than throw reading a property off undefined.

        await mountWithCleanup(WebClient);

        await expect.waitForSteps(["selectMenu:1"]);
    }
);

test(
    "apps_menu service unavailable entirely -> WebClient still boots into the standard " +
        "destination without throwing",
    async () => {
        mockMenuService();
        // Deliberately do NOT register "apps_menu": this is the isolated core-component scenario
        // 221946b exists to protect (WebClient mounted in an env where web_responsive's apps_menu
        // service never started, e.g. core mail's stripped-down multi-tab test env). The
        // preference is left "on" on purpose - even when the user wants the Apps menu, the guard
        // must still fall back safely when the service itself is missing. The services registry is
        // snapshotted/restored around every test (env_test_helpers.js), so this removal never
        // leaks into other tests.
        registry.category("services").remove("apps_menu");
        patchWithCleanup(session, { apps_menu: { is_redirect_home: true } });

        await mountWithCleanup(WebClient);

        await expect.waitForSteps(["selectMenu:1"]);
    }
);
