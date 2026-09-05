/* Copyright 2018 Tecnativa - Jairo Llopis
 * Copyright 2021 ITerra - Sergey Shebanin
 * Copyright 2023 Onestein - Anjeel Haria
 * Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import {Component, useState} from "@odoo/owl";
import {useAutofocus, useService} from "@web/core/utils/hooks";
import {patch} from "@web/core/utils/patch";

/**
 * @extends Component
 * @property {{el: HTMLInputElement}} searchBarInput
 */
export class AppsMenuOdooSearchBar extends Component {
    static template = "web_responsive.AppsMenuOdooSearchBar";
    static props = {dismiss: Function};
    setup() {
        super.setup();
        this.state = useState({
            rootItems: [],
            subItems: [],
            offset: 0,
            hasResults: false,
        });
        this.searchBarInput = useAutofocus({refName: "SearchBarInput"});
        this.command = useService("command");
        this.menuService = useService("menu");
        this._paletteDismissTracking = false;
    }

    /**
     * @returns {String}
     */
    get inputValue() {
        const {el} = this.searchBarInput;
        return el ? el.value : "";
    }

    set inputValue(value) {
        const {el} = this.searchBarInput;
        if (el) {
            el.value = value;
        }
    }

    _onSearchInput() {
        if (this.inputValue) {
            this._openSearchMenu(this.inputValue);
            this.inputValue = "";
        }
    }

    _onSearchClick() {
        this._openSearchMenu();
    }

    /**
     * @param {String} [value]
     * @private
     */
    _openSearchMenu(value) {
        const searchValue = value ? `/${value}` : "/";
        // core's command service drops onClose on every call after the first while its palette
        // stays open, so re-passing it here per keystroke would orphan a patch() layer per call.
        if (this._paletteDismissTracking) {
            this.command.openMainPalette({searchValue});
            return;
        }
        this._paletteDismissTracking = true;
        // openMainPalette's onClose fires on every dialog close, selection or Escape alike, so
        // only a menu actually having been selected may dismiss the apps-menu overlay.
        let menuWasSelected = false;
        const unpatch = patch(this.menuService, {
            selectMenu(menu) {
                menuWasSelected = true;
                return super.selectMenu(menu);
            },
        });
        this.command.openMainPalette({searchValue}, () => {
            this._paletteDismissTracking = false;
            unpatch();
            if (menuWasSelected) {
                this.props.dismiss();
            }
        });
    }
}

