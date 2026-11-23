// Shared app-icon resolver for the home menu.
//
// Odoo apps declare either an image icon, `web_icon="<module>,static/description/icon.png"`, or a
// built icon, `web_icon="<icon name>,<color>,<background color>"`; the menu service exposes that
// string on `app.webIcon` and the image's data-URI on `app.webIconData`. The comma-prefix of an image
// icon is the app's technical name, which matches the file names in
// `viin_brand/static/img/apps/<name>.png`. The Viindoo icon is preferred for a consistent branded
// look; the app's own `webIconData` (core's default_icon_app.png placeholder included) is the
// fallback. A built icon has no image: the home menu draws its glyph as core's own menus do.

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
 * Return the parts of a built icon (`<icon name>,<color>,<background color>`), or null for an
 * image icon or an app without icon.
 * @param {object} app a menu-service app entry ({ webIcon, webIconData, ... })
 * @returns {{icon: string, color: string, background: string} | null}
 */
export function getBuiltIcon(app) {
    const parts = ((app && app.webIcon) || "").split(",");
    if (parts.length !== 3) {
        return null;
    }
    const [icon, color, background] = parts.map((part) => part.trim());
    return { icon, color, background };
}

/**
 * Return the technical (module) name an app's image icon points at, or "".
 * @param {object} app a menu-service app entry ({ webIcon, webIconData, ... })
 * @returns {string}
 */
export function appIconModule(app) {
    if (getBuiltIcon(app)) {
        return "";
    }
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
