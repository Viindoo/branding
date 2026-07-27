/** @odoo-module **/

// R1 (PR #658) - make core's clickbot navigate apps via the theme's flat home menu.
//
// PROBLEM (proven: TestMenusDemoLight.test_01_click_apps_menus_as_demo fails on the themed build,
// stock passes). The theme repurposed `.o_navbar_apps_menu`'s inner core <Dropdown> (apps_menu_home.xml)
// with a plain button that opens the ONE home menu, so core's clickbot community path
// (web/static/src/webclient/clickbot/clickbot.js) finds no `.o_navbar_apps_menu .dropdown-toggle`
// (the class core's Dropdown pushes - dropdown.js:278) and throws
// `No element "apps menu toggle button" found`; its `.o-dropdown--menu .o_app` / `.dropdown-item`
// selectors are likewise gone.
//
// PATCHABILITY (grounded, OSM 19.0 + core source). clickbot.js exposes ONLY `window.clickEverywhere`;
// its app-enumeration functions (ensureAppsMenu / getNextApp / testApp) are module-private CLOSURES -
// not exported, not on a class prototype, not in a registry - so an OWL `patch()` cannot reach them.
// The one honest module-side seam is `window.clickEverywhere`, which the LAZY `web.assets_clickbot`
// bundle assigns at run time (loaded on demand by clickbot_loader.startClickEverywhere). This eager
// web.assets_backend file therefore installs an accessor on `window.clickEverywhere` to capture that
// late assignment (the core function) and hand callers a theme-aware wrapper instead.
//
// BEHAVIOUR. When the theme apps-menu is active (core's `.dropdown-toggle` is gone), the wrapper walks
// apps through the home menu: click `.o_navbar_apps_menu button` to open the ONE home menu, then
// enumerate/click `.o_viin_home_menu .o_app[data-menu-xmlid]` tiles (home_menu.xml), faithfully
// reproducing the clickbot's observable contract - settle on pending RPCs + the OWL scheduler, close
// modals, and throw on `.o_error_dialog` (so a broken app still fails the test). For FULL mode it
// pre-marks the opened app "tested" and hands drilling back to the untouched core clickbot, which then
// reuses its own menu/view/filter crawl on theme-safe selectors (`.o_menu_sections`,
// `.o_cp_switch_buttons`) without re-opening via the removed dropdown. On any non-themed shell
// (theme-free / enterprise / scoped app) it delegates verbatim to core - so the theme-free path is
// untouched.

import { App } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { rpcBus } from "@web/core/network/rpc";

// Core's public success contract (clickbot.js SUCCESS_SIGNAL) + blacklist, duplicated as literals
// (NOT imported) so this eager backend file never force-loads the lazy clickbot module.
const SUCCESS_SIGNAL = "clickbot test succeeded";
const MOUSE_EVENTS = ["mouseover", "mouseenter", "mousedown", "mouseup", "click"];
const BLACKLISTED_MENUS = [
    "base.menu_theme_store",
    "base.menu_third_party",
    "event.menu_event_registration_desk",
    "hr_attendance.menu_action_open_form",
    "hr_attendance.menu_hr_attendance_onboarding",
    "mrp_workorder.menu_mrp_workorder_root",
    "pos_enterprise.menu_point_kitchen_display_root",
];

const HOME_TILE = ".o_viin_home_menu .o_app[data-menu-xmlid]";
const APPS_BUTTON = ".o_navbar_apps_menu button";
const CORE_TOGGLE = ".o_navbar_apps_menu .dropdown-toggle";

// --- settle / error tracking (mirrors clickbot.js waitForCondition) -----------------------------
let calledRPC = {};
let errorRPC;

function onRPCRequest({ detail }) {
    calledRPC[detail.data.id] = detail.url;
}

function onRPCResponse({ detail }) {
    delete calledRPC[detail.data.id];
    if (detail.error) {
        errorRPC = { ...detail };
    }
}

function hasPendingRPC() {
    return Object.keys(calledRPC).length > 0;
}

function hasScheduledTask() {
    let size = 0;
    for (const app of App.apps) {
        size += app.scheduler.tasks.size;
    }
    return size > 0;
}

function errorDialog() {
    const dialog = document.querySelector(".o_error_dialog");
    if (dialog) {
        if (errorRPC) {
            browser.console.error(
                "A RPC in error was detected, maybe it's related to the error dialog : " +
                    JSON.stringify(errorRPC)
            );
        }
        throw new Error("Error dialog detected" + dialog.innerHTML);
    }
    return false;
}

async function waitForNextAnimationFrame() {
    await new Promise((resolve) => browser.setTimeout(resolve));
    await new Promise((resolve) => requestAnimationFrame(resolve));
}

async function triggerClick(target, description) {
    if (!target) {
        throw new Error(`No element "${description}" found.`);
    }
    browser.console.log(`Clicking on: ${description}`);
    for (const type of MOUSE_EVENTS) {
        target.dispatchEvent(
            new MouseEvent(type, { bubbles: true, cancelable: true, view: window })
        );
    }
    await waitForNextAnimationFrame();
}

async function waitForCondition(stopCondition) {
    const interval = 25;
    let timeLimit = 30000;
    while (errorDialog() || !stopCondition() || hasPendingRPC() || hasScheduledTask()) {
        if (timeLimit <= 0) {
            throw new Error("Timeout while waiting for the themed home-menu walk to settle (30s).");
        }
        await new Promise((resolve) => browser.setTimeout(resolve, interval));
        timeLimit -= interval;
    }
}

// --- home-menu navigation -----------------------------------------------------------------------
async function ensureHomeMenuOpen() {
    if (document.querySelector(HOME_TILE)) {
        return; // themed /odoo already landed on the home menu, or it is still open
    }
    await triggerClick(document.querySelector(APPS_BUTTON), "apps menu toggle button");
    await waitForCondition(() => Boolean(document.querySelector(HOME_TILE)));
}

async function enumerateApps() {
    await ensureHomeMenuOpen();
    return [...document.querySelectorAll(HOME_TILE)]
        .map((tile) => tile.dataset.menuXmlid)
        .filter((xmlid) => xmlid && !BLACKLISTED_MENUS.includes(xmlid));
}

async function openApp(xmlid) {
    await ensureHomeMenuOpen();
    const tile = document.querySelector(`.o_viin_home_menu .o_app[data-menu-xmlid="${xmlid}"]`);
    let isModal = false;
    await triggerClick(tile, `home-menu app tile "${xmlid}"`);
    // Settle: a modal opened, or the home menu was replaced by the app - AND no pending RPC / OWL
    // scheduler task remains (waitForCondition), so an async render error still surfaces.
    await waitForCondition(() => {
        if (document.querySelector(".o_dialog:not(.o_error_dialog)")) {
            isModal = true;
            return true;
        }
        return !document.querySelector(HOME_TILE);
    });
    if (isModal) {
        await triggerClick(
            document.querySelector(".o_dialog header > .btn-close"),
            "modal close button"
        );
        await waitForCondition(() => !document.querySelector(".o_dialog:not(.o_error_dialog)"));
    }
}

// FULL-mode drilling is delegated to the untouched core clickbot: pre-mark the app tested so core
// skips its (removed) dropdown open and drills only its theme-safe menu/view/filter selectors.
function drillState(xmlid) {
    return {
        light: false,
        app: xmlid,
        xmlId: xmlid,
        testedApps: [xmlid],
        studioCount: 0,
        testedMenus: [xmlid],
        testedFilters: 0,
        testedModals: 0,
        appIndex: 0,
        menuIndex: 0,
        subMenuIndex: 0,
    };
}

async function viinClickEverywhere(xmlId, light, core) {
    calledRPC = {};
    errorRPC = undefined;
    rpcBus.addEventListener("RPC:REQUEST", onRPCRequest);
    rpcBus.addEventListener("RPC:RESPONSE", onRPCResponse);
    browser.console.log("Starting ClickEverywhere test (Viindoo themed home-menu walk)");
    const startTime = performance.now();
    try {
        const xmlids = xmlId ? [xmlId] : await enumerateApps();
        let tested = 0;
        for (const id of xmlids) {
            if (BLACKLISTED_MENUS.includes(id)) {
                continue;
            }
            browser.console.log(`Testing app menu: ${id}`);
            await openApp(id);
            tested++;
            if (!light && core) {
                await core(id, false, drillState(id));
            }
        }
        browser.console.log(`Test took ${(performance.now() - startTime) / 1000} seconds`);
        browser.console.log(`Successfully tested ${tested} apps`);
        browser.console.log(SUCCESS_SIGNAL);
    } catch (err) {
        browser.console.log(`Test took ${(performance.now() - startTime) / 1000} seconds`);
        browser.console.error(err || "test failed");
    } finally {
        rpcBus.removeEventListener("RPC:REQUEST", onRPCRequest);
        rpcBus.removeEventListener("RPC:RESPONSE", onRPCResponse);
    }
}

// --- install the accessor seam on window.clickEverywhere ----------------------------------------
// themed = core's apps-menu <Dropdown> toggle is gone (the theme replaced it with the home-menu
// button). The presence of the button plus the absence of `.dropdown-toggle` is the exact signal
// that broke the community clickbot path, so it is the right discriminator.
function isThemedShell() {
    return Boolean(document.querySelector(APPS_BUTTON)) && !document.querySelector(CORE_TOGGLE);
}

let coreClickEverywhere = null;

function clickEverywhereWrapper(xmlId, light, currentState) {
    if (!isThemedShell()) {
        // theme-free / enterprise / scoped app: run core verbatim (incl. reload-resume state).
        return coreClickEverywhere ? coreClickEverywhere(xmlId, light, currentState) : undefined;
    }
    // Themed: walk via the home menu. A reload-resume `currentState` is core's dropdown-shaped
    // state we do not consume; a fresh idempotent walk is correct for the "opens without error"
    // contract (light mode never triggers a full reload, so this is a defensive fallback).
    return viinClickEverywhere(xmlId, light, coreClickEverywhere);
}

Object.defineProperty(window, "clickEverywhere", {
    configurable: true,
    get() {
        return clickEverywhereWrapper;
    },
    set(fn) {
        coreClickEverywhere = fn;
    },
});
