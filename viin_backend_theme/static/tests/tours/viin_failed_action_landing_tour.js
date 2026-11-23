// Guards: when the action of the URL fails to load, the landing is the home menu alone, as the stock
// landing is the first app alone: no error dialog stays over it and no breadcrumb of the failed
// action stays under it, whenever the error reaches the page. Driven by tests/test_tours.py.
//
// The failed load reaches the error service as an unhandled rejection, which the service marks as
// handled when it takes the error. The assertions wait for that, so that they never read the page
// before the error of the failed load has reached it.
//
// `?viin_error_delay=<ms>` on the URL holds that rejection back for that many milliseconds before
// the error service sees it, so the error reaches the page as late as the test chooses: before the
// landing is done (0) or long after it.

import { registry } from "@web/core/registry";
import { RPCError, rpc } from "@web/core/network/rpc";

const delayParam = new URLSearchParams(window.location.search).get("viin_error_delay");
const delay = delayParam === null ? null : Number(delayParam);

// Recorded when the bundle loads, before the web client starts the failing action.
let failedLoad = null;
window.addEventListener(
    "unhandledrejection",
    (event) => {
        if (!(event.reason instanceof RPCError)) {
            return;
        }
        if (delay !== null && !event.viinDelayed) {
            // The capture listener of the window runs before the one of the error service.
            event.stopImmediatePropagation();
            event.preventDefault();
            setTimeout(() => {
                const delayed = new PromiseRejectionEvent("unhandledrejection", {
                    promise: event.promise,
                    reason: event.reason,
                    cancelable: true,
                });
                delayed.viinDelayed = true;
                failedLoad = delayed;
                window.dispatchEvent(delayed);
            }, delay);
            return;
        }
        failedLoad ||= event;
    },
    { capture: true }
);

const nextFrame = () => new Promise((resolve) => requestAnimationFrame(resolve));

// A request of the model of the failing action that the server refuses, left unhandled as the error
// of a button of the page is: its error opens the dialog of the error service.
const failRequest = () =>
    rpc("/web/dataset/call_kw/res.partner/web_search_read", {
        model: "res.partner",
        method: "web_search_read",
        args: [[["x_no_such_field", "=", 1]]],
        kwargs: { specification: { name: {} } },
    });

const expectErrorDialog = {
    content: "a later error of the same model still opens its dialog",
    trigger: ".modal .o_error_dialog",
};

registry.category("web_tour.tours").add("viin_failed_action_landing_tour", {
    steps: () => [
        {
            content: "the home menu is the landing of the failed action",
            trigger: ".o_viin_home_menu",
        },
        {
            content: "no dialog stays over the landing, once the error of the failed load is shown",
            trigger: "body",
            run: async () => {
                const deadline = performance.now() + 20000;
                while (!failedLoad?.defaultPrevented) {
                    if (performance.now() > deadline) {
                        throw new Error(
                            "the error of the failed load never reached the error service"
                        );
                    }
                    await nextFrame();
                }
                // the dialog the service opened renders on the frame that follows
                await nextFrame();
                await nextFrame();
                const dialogs = document.querySelectorAll(".modal").length;
                if (dialogs) {
                    throw new Error(`expected no dialog over the landing, found ${dialogs}`);
                }
            },
        },
        {
            content: "the failed action is not in the URL",
            trigger: "body",
            run: () => {
                const path = window.location.pathname;
                if (path !== "/odoo/viin_home_menu") {
                    throw new Error(`expected the landing alone in the URL, found ${path}`);
                }
            },
        },
        {
            content: "an error of the same model that comes after the landing is not taken",
            trigger: "body",
            run: () => {
                failRequest();
            },
        },
        expectErrorDialog,
    ],
});

registry.category("web_tour.tours").add("viin_landing_error_dialog_tour", {
    steps: () => [
        {
            content: "the home menu is the landing of the boot",
            trigger: ".o_viin_home_menu",
        },
        {
            content: "an error of a request opens its dialog over the boot landing",
            trigger: "body",
            run: () => {
                failRequest();
            },
        },
        {
            content: "the error dialog is open",
            trigger: ".modal .o_error_dialog",
        },
    ],
});

registry.category("web_tour.tours").add("viin_missing_action_landing_tour", {
    steps: () => [
        {
            content: "the list of an action that loads",
            trigger: ".o_list_renderer",
        },
        {
            content: "the history goes to an action that does not exist",
            trigger: "body",
            run: () => {
                window.history.pushState({}, "", "/odoo/viin-missing-action");
                window.dispatchEvent(new PopStateEvent("popstate", { state: {} }));
            },
        },
        {
            content: "the home menu is the landing of the missing action",
            trigger: ".o_viin_home_menu",
        },
        {
            content: "the user acts on the page",
            trigger: "body",
            run: () => {
                document.body.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true }));
            },
        },
        {
            content: "an error of the model of the replaced list that comes after is not taken",
            trigger: "body",
            run: () => {
                failRequest();
            },
        },
        expectErrorDialog,
    ],
});
