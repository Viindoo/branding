/** @odoo-module **/

// W4 unit-b - ViinAppearanceSystray: navbar systray dropdown for the appearance controls (mockup-25
// moon icon). Offers the color-scheme choice (Light / Dark / System) + the density choice
// (Comfortable / Compact), delegating every change to the viin_theme service (the single applier +
// persister). TDD §4b: a NEW component (registry systray with an explicit sequence), NOT a patch.
// Keyboard + aria accessible via the core Dropdown/DropdownItem (role=menuitemradio + aria-checked).

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class ViinAppearanceSystray extends Component {
    static template = "viin_backend_theme.ViinAppearanceSystray";
    static components = { Dropdown, DropdownItem };
    static props = {};

    setup() {
        this.viinTheme = useService("viin_theme");
        // Wrap the service's reactive state so the selected-option indicator re-renders on change.
        this.state = useState(this.viinTheme.state);
        this.schemes = [
            { value: "light", label: _t("Light"), icon: "fa-sun-o" },
            { value: "dark", label: _t("Dark"), icon: "fa-moon-o" },
            { value: "auto", label: _t("System"), icon: "fa-desktop" },
        ];
        this.densities = [
            { value: "comfortable", label: _t("Comfortable"), icon: "fa-bars" },
            { value: "compact", label: _t("Compact"), icon: "fa-th-list" },
        ];
    }

    setScheme(value) {
        this.viinTheme.setScheme(value);
    }

    setDensity(value) {
        this.viinTheme.setDensity(value);
    }
}

// Explicit sequence (TDD §4b). systrayItems = registry.getEntries() (sequence ascending) THEN
// .reverse() (navbar.js), so a HIGHER sequence renders further LEFT. 30 places the appearance toggle
// left of the mail messaging (25) / activity (20) menus - near the mockup's moon position - and right
// of a call menu (100). SwitchCompanyMenu (1) / user menu (0) stay rightmost.
registry
    .category("systray")
    .add("viin_backend_theme.appearance", { Component: ViinAppearanceSystray }, { sequence: 30 });
