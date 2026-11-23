import "@web/webclient/user_menu/user_menu_items";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

function documentationItem() {
    // The series comes from the running server, like core's DocumentationLink, so the link never
    // targets a stale series. Unlike core, a non-final build keeps its numeric series: the
    // viindoo.com documentation tree has no "master".
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

function supportItem() {
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

function viindooAccountItem() {
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

user_menuitems
    .add("viindoo_documentation", documentationItem)
    .add("viindoo_support", supportItem)
    .add("viindoo_account", viindooAccountItem);
