/** @odoo-module **/

import "@web/webclient/user_menu/user_menu_items";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

function documentationItem(env) {
    // Series segment derived from the RUNNING server, never pinned. `odoo/release.py:16` builds
    // `series` as '.'.join(version_info[:2]), and core's own DocumentationLink widget derives its
    // documentation URL's version segment from that same `session.server_version_info`
    // (web/static/src/views/widgets/documentation_link/documentation_link.js:22-29). A pinned
    // literal is a silent footgun: a forward-port that forgets to bump it ships a wrong-series
    // documentation link - nothing raises, the link just lands on the wrong (or missing) series.
    // `server_version_info` is unconditionally part of session_info (web/models/ir_http.py:108),
    // so it is read unguarded here, exactly as core reads it.
    // Deliberate deviation from core: core falls back to "master" for a non-final build because
    // odoo.com publishes a /documentation/master/ tree. viindoo.com/documentation is series-based
    // and this link has always rendered a concrete series, so no "master" branch is introduced.
    // The "~" -> "-" normalisation is core's own, and a no-op for a numeric series.
    const series = `${session.server_version_info[0]}.${session.server_version_info[1]}`.replace(
        "~",
        "-"
    );
    const documentationURL = `https://viindoo.com/documentation/${series}/`;
    return {
        type: "item",
        id: "documentation",
        description: _t("Documentation"),
        href: documentationURL,
        callback: () => {
            browser.open(documentationURL, "_blank");
        },
        sequence: 10,
    };
}

function supportItem(env) {
    const url = "https://viindoo.com/ticket";
    return {
        type: "item",
        id: "support",
        description: _t("Support"),
        href: url,
        callback: () => {
            browser.open(url, "_blank");
        },
        sequence: 20,
    };
}

function viindooAccountItem(env) {
    const viindooURL = "https://viindoo.com/my";
    return {
        type: "item",
        id: "account",
        description: _t("My Viindoo.com account"),
        href: viindooURL,
        callback: () => {
            browser.open(viindooURL, "_blank");
        },
        sequence: 60,
    };
}

const user_menuitems = registry.category("user_menuitems");
user_menuitems.remove("support");
user_menuitems.remove("odoo_account");

user_menuitems
    .add("viindoo_documentation", documentationItem)
    .add("viindoo_support", supportItem)
    .add("viindoo_account", viindooAccountItem);
