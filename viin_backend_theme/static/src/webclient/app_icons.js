/** @odoo-module **/

// Shared app-icon resolver for the home menu.
//
// Odoo apps declare `web_icon="<module>,static/description/icon.png"`; the menu service exposes that
// string on `app.webIcon` and its rendered data-URI on `app.webIconData`. The comma-prefix is the
// app's technical name, which matches the file names in `viin_brand/static/img/apps/<name>.png`. The
// Viindoo icon is preferred for a consistent branded look; the app's own `webIconData` (core's
// default_icon_app.png placeholder included) is the fallback, and font-glyph apps (a non-module
// first token such as "fa fa-...") fall through to it as well.

// Names of the icons in viin_brand/static/img/apps/; a miss means "use the native icon", never a
// broken image.
export const VIIN_APP_ICONS = new Set([
    "account",
    "base",
    "board",
    "calendar",
    "contacts",
    "crm",
    "data_recycle",
    "event",
    "fleet",
    "hr",
    "hr_attendance",
    "hr_contract",
    "hr_expense",
    "hr_holidays",
    "hr_recruitment",
    "hr_skills",
    "hr_timesheet",
    "im_livechat",
    "lunch",
    "mail",
    "mail_bot",
    "maintenance",
    "mass_mailing",
    "mass_mailing_sms",
    "membership",
    "mrp",
    "note",
    "point_of_sale",
    "pos_restaurant",
    "product",
    "project",
    "project_todo",
    "purchase",
    "repair",
    "sale",
    "sale_management",
    "settings",
    "sms",
    "spreadsheet_dashboard",
    "spreadsheet_oca",
    "stock",
    "survey",
    "utm",
    "website",
    "website_blog",
    "website_event",
    "website_forum",
    "website_hr_recruitment",
    "website_links",
    "website_livechat",
    "website_sale",
    "website_sale_loyalty",
    "website_slides",
]);

/**
 * Return the technical (module) name an app's web_icon points at, or "".
 * @param {object} app a menu-service app entry ({ webIcon, webIconData, ... })
 * @returns {string}
 */
export function appIconModule(app) {
    return ((app && app.webIcon) || "").split(",")[0].trim();
}

/**
 * Resolve the best icon URL for an app: the branded Viindoo PNG when one exists for the app's
 * module, otherwise the app's native `webIconData` data-URI (already carries core's own fallback).
 * @param {object} app a menu-service app entry
 * @returns {string} a src usable on <img>
 */
export function getAppIconUrl(app) {
    const mod = appIconModule(app);
    if (mod && VIIN_APP_ICONS.has(mod)) {
        return `/viin_brand/static/img/apps/${mod}.png`;
    }
    return (app && app.webIconData) || "/web/static/img/default_icon_app.png";
}
