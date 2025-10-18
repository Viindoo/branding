import * as appsMenuTools from "@web_responsive/components/apps_menu_tools.esm";

appsMenuTools.getWebIconData = function(menu) {
    const result = "/web_responsive/static/img/default_icon_app.png";
    const iconData = menu.webIconData;
    if (!iconData) {
        return result;
    }
    const prefix = iconData.startsWith("P")
        ? "data:image/svg+xml;base64,"
        : "data:image/png;base64,";
    if (iconData.startsWith("data:image")) {
        return iconData;
    }
    return prefix + iconData.replace(/\s/g, "");
}