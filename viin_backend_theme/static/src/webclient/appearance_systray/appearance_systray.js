// ViinAppearanceSystray: navbar systray dropdown for the appearance controls. Offers the color-scheme
// choice (Light / Dark / System) and the density choice (Comfortable / Compact), delegating every
// change to the ViinThemePlugin, the single applier and persister. Keyboard and aria accessible
// through the core Dropdown/DropdownItem (role=menuitemradio + aria-checked).

import { Component, usePlugin, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ViinThemePlugin } from "../viin_theme_plugin";

export class ViinAppearanceSystray extends Component {
    static template = "viin_backend_theme.ViinAppearanceSystray";
    static components = { Dropdown, DropdownItem };
    props = useProps({});
    viinTheme = usePlugin(ViinThemePlugin);

    setup() {
        this.schemes = [
            { value: "light", label: _t("Light"), icon: "light_mode" },
            { value: "dark", label: _t("Dark"), icon: "dark_mode" },
            { value: "auto", label: _t("System"), icon: "desktop_windows" },
        ];
        this.densities = [
            { value: "comfortable", label: _t("Comfortable"), icon: "menu" },
            { value: "compact", label: _t("Compact"), icon: "view_list" },
        ];
    }

    setScheme(value) {
        this.viinTheme.setScheme(value);
    }

    setDensity(value) {
        this.viinTheme.setDensity(value);
    }
}

// systrayItems = registry.getEntries() (sequence ascending) then .reverse() (navbar.js), so a higher
// sequence renders further left. 30 places the appearance toggle left of the mail messaging (25) and
// activity (20) menus and right of a call menu (100); SwitchCompanyMenu (1) and the user menu (0)
// stay rightmost.
registry
    .category("systray")
    .add("viin_backend_theme.appearance", { Component: ViinAppearanceSystray }, { sequence: 30 });
