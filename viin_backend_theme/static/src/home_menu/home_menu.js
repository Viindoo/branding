/** @odoo-module **/

// ViinHomeMenu: the flat "Applications" grid (client action tag "viin_home_menu"). One dense grid
// with no category sections. Search-first: filters with the core fuzzyLookup; the arrow keys move a
// highlight across the responsive grid and Enter launches the highlighted app. Icons load lazily.
// Reads the native menuService app list and launches via menuService.selectMenu.
//
// Per-user drag-reorder: the grid is ordered by the user's stored res.users.viin_home_app_order (app
// root-menu xmlids); a press-drag reorders the tiles and persists the new order to that
// self-writeable field. Apps missing from the stored order (newly installed) append at the end in
// default sequence and are never hidden.
//
// Search-first focus: `onMounted` pre-focuses the search box in both render shapes when `hasTouch`
// reports no touch support, so the user can type at once. Recovering a keystroke that arrives after
// focus moved elsewhere (`onWindowKeydown`) needs the box to hold focus already, so an IME
// composition can attach to it and the native keydown appends rather than overwrites.
//
// The search box therefore takes the page's first Tab instead of the shell's `.o_viin_skip_link`
// (WCAG 2.4.1); the skip link stays reachable by Shift-Tab, and the input's `aria-label`
// (home_menu.xml) tells a screen-reader user what the field is. `data-allow-hotkeys="true"` keeps
// core's global hotkeys reachable while the box holds focus (hotkey_service.js
// `shouldProtectEditable`). `role="combobox"` is not used: it implies aria-expanded/aria-controls/
// aria-activedescendant wiring for a popup listbox, and this grid is always visible.
//
// Two mount points, one component: the navbar apps button renders it through the overlay service
// above the still-mounted controller (core's contract for that button is to open a list, not to
// navigate, which core tours built on `stepUtils.showAppsMenuItem()` rely on), and the client action
// serves the boot landing, where there is no controller to preserve.
//
// The tiles are `<a href>`, as core renders its own app list: middle-click opens a new tab,
// right-click copies the link, and a screen reader announces a link.

import {
    Component,
    useState,
    useRef,
    useExternalListener,
    onMounted,
    onWillStart,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { hasTouch } from "@web/core/browser/feature_detection";
import { useBus, useService } from "@web/core/utils/hooks";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { useSortable } from "@web/core/utils/sortable_owl";
import { normalize } from "@web/core/l10n/utils";
import { fuzzyLookup } from "@web/core/utils/search";
import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";
import { routerBus } from "@web/core/browser/router";
import { NavBar } from "@web/webclient/navbar/navbar";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { getAppIconUrl } from "../webclient/app_icons";

// Navbar chrome the overlay must not treat as "outside": clicking the apps button toggles the
// overlay, and a pointerdown-close would shut it a beat before the click re-opened it. On a small
// screen core renders the toggle as `a.o_menu_toggle`.
const APPS_MENU_SELECTOR = ".o_navbar_apps_menu, .o_menu_toggle";

const { DateTime } = luxon;

// Menu items are searched from this many characters: a single letter fuzzy-matches nearly every
// menu entry, which is noise rather than a result (apps are still searched from one character).
const MENU_SEARCH_MIN_LENGTH = 2;
const MENU_SEARCH_MAX_RESULTS = 15;

export class ViinHomeMenu extends Component {
    static template = "viin_backend_theme.ViinHomeMenu";
    // Rendered either as the boot-landing client action (action-service props below) or as the
    // overlay the navbar apps button opens (`close` set, no action), so `action` is optional.
    static props = {
        ...standardActionServiceProps,
        action: { type: Object, optional: true },
        close: { type: Function, optional: true },
    };

    setup() {
        this.menuService = useService("menu");
        this.orm = useService("orm");
        this.ui = useService("ui");
        this.gridRef = useRef("grid");
        this.searchRef = useRef("search");
        // Pre-focus the search box on mount in either render shape (see the file header); skipped on
        // a touch device, where an unrequested virtual keyboard is worse than no focus.
        onMounted(() => {
            if (!hasTouch()) {
                this._focusSearchInput();
            }
        });
        // Type-to-search recovery: a printable keystroke with nothing editable focused moves focus
        // back into the search box, in either render shape. useHotkey cannot express "any printable
        // character", so this listens directly and mirrors hotkey_service.js: the IME-composition
        // check, the targetIsEditable rule (an already-focused editable keeps its native typing) and
        // the `ui.activeElement` check (a Dialog or higher layer owns the keystroke).
        useExternalListener(window, "keydown", this.onWindowKeydown);
        if (this.isOverlay) {
            // Dismissal as core's apps dropdown does it (`closeOnClickAway`, no backdrop): a pointer
            // interaction outside both the overlay and the navbar apps button closes it, so the
            // page underneath stays usable and a tour's next click does not hit a stranded panel.
            useExternalListener(document, "pointerdown", this.onOutsidePointerDown, {
                capture: true,
            });
            // Whatever sits above the navbar can change height with the window (a banner wrapping),
            // so the measured top edge is measured again.
            useExternalListener(window, "resize", () => this.render());
            // Escape dismisses and returns focus to the opening button: a non-modal overlay must
            // not trap the user (WCAG 2.1.2). The client-action arm has no trigger to return to.
            useHotkey("escape", () => this.props.close({ restoreFocus: true }), {
                bypassEditableProtection: true,
            });
            // Browser Back/Forward re-points the webclient behind the overlay, leaving the screen and
            // the address bar disagreeing. Nothing of ours navigates while it is open, so any route
            // change means the user left it: put it away.
            useBus(routerBus, "ROUTE_CHANGE", () => this.props.close());
        }
        this.state = useState({
            query: "",
            // index of the highlighted tile within `filteredApps` (arrow-nav), -1 = none
            focusIndex: -1,
            // per-user tile order (app root-menu xmlids); [] = default menu sequence
            appOrder: [],
            // csv of the last order the server acknowledged, surfaced on the grid as
            // data-viin-saved-order so a caller can tell when a drop has persisted
            savedOrder: null,
        });
        // Press-drag reorders the grid. A movement tolerance (not a press-delay) tells a plain tap
        // (launches the app) from a drag, which sets the sortable's preventClick so the dragged tile
        // never launches on drop. Disabled while searching: the filtered subset is not the persisted
        // order.
        useSortable({
            enable: () => !this.state.query,
            ref: this.gridRef,
            elements: ".o_viin_home_app",
            cursor: "move",
            tolerance: 10,
            onDrop: (params) => this.onTileDrop(params),
        });
        // Subtitle "<date> - N activities due today" (today-or-earlier, as Odoo's "today" activity
        // meaning includes overdue) and the stored app order, read together. Each read degrades on its
        // own, so a failure never blanks the grid: 0 activities, default-sequence order.
        this.activityCount = 0;
        onWillStart(async () => {
            // "en-CA" yields the ISO date (YYYY-MM-DD) of the local day (not UTC), avoiding a midnight
            // off-by-one in the server domain.
            const today = new Date().toLocaleDateString("en-CA");
            const [activityCount, appOrder] = await Promise.all([
                this.orm
                    .searchCount("mail.activity", [
                        ["user_id", "=", user.userId],
                        ["date_deadline", "<=", today],
                    ])
                    .catch(() => 0),
                this.orm
                    .read("res.users", [user.userId], ["viin_home_app_order"])
                    .then((records) => this._parseOrder(records[0]?.viin_home_app_order))
                    .catch(() => []),
            ]);
            this.activityCount = activityCount;
            this.state.appOrder = appOrder;
        });
    }

    /** Rendered as the navbar's non-navigating overlay rather than as the boot-landing page? */
    get isOverlay() {
        return Boolean(this.props.close);
    }

    /**
     * The overlay starts at the navbar's real bottom edge, not at its height: anything rendered above
     * the navbar (a banner) pushes it down. Without a navbar the panel starts at the window top.
     */
    get overlayStyle() {
        if (!this.isOverlay) {
            return "";
        }
        const navbar = document.querySelector("header.o_navbar");
        const top = navbar ? Math.max(0, Math.round(navbar.getBoundingClientRect().bottom)) : 0;
        return `top: ${top}px`;
    }

    get apps() {
        return this._orderApps(this.menuService.getApps());
    }

    /** Close the overlay when the user interacts with anything it does not own.
     *  A no-op on the client-action arm, which never registers the listener. */
    onOutsidePointerDown(ev) {
        const target = ev.target;
        if (!(target instanceof Element)) {
            return;
        }
        if (target.closest(".o_viin_home_overlay") || target.closest(APPS_MENU_SELECTOR)) {
            return;
        }
        this.props.close();
    }

    /** The tile's `href`, from core's `NavBar.prototype.getMenuItemHref`, the single definition of an
     *  app's backend URL (`/odoo/<actionPath|action-<id>>`). It reads nothing off `this`, so calling
     *  it through the prototype is safe. */
    getMenuHref(app) {
        return NavBar.prototype.getMenuItemHref(app);
    }

    /** Parse the stored csv of app root-menu xmlids into a clean list (blank entries dropped). */
    _parseOrder(csv) {
        if (!csv) {
            return [];
        }
        return csv
            .split(",")
            .map((xmlid) => xmlid.trim())
            .filter(Boolean);
    }

    /** Order apps by the per-user preference (state.appOrder): apps in the stored order come first,
     *  in that order; the rest keep the default menu sequence and append at the end. Never filters,
     *  so a stale stored value cannot hide an app. */
    _orderApps(apps) {
        const rank = new Map(this.state.appOrder.map((xmlid, index) => [xmlid, index]));
        return apps
            .map((app, index) => ({ app, index }))
            .sort((a, b) => {
                const ra = rank.has(a.app.xmlid) ? rank.get(a.app.xmlid) : Infinity;
                const rb = rank.has(b.app.xmlid) ? rank.get(b.app.xmlid) : Infinity;
                // Equal rank (both unknown): keep the default menu sequence.
                return ra === rb ? a.index - b.index : ra - rb;
            })
            .map((entry) => entry.app);
    }

    /** On drop, splice the dragged tile to its new slot (after `previous`, or first if none), rewrite
     *  the reactive order so the grid re-renders, then persist it. */
    onTileDrop({ element, previous }) {
        const xmlid = element.dataset.menuXmlid;
        if (!xmlid) {
            return;
        }
        const order = this.apps.map((app) => app.xmlid);
        const from = order.indexOf(xmlid);
        if (from >= 0) {
            order.splice(from, 1);
        }
        if (previous) {
            const prevIndex = order.indexOf(previous.dataset.menuXmlid);
            order.splice(prevIndex + 1, 0, xmlid);
        } else {
            order.splice(0, 0, xmlid);
        }
        this.state.appOrder = order;
        this._persistOrder(order);
    }

    /** Persist the reordered app list to the user's self-writeable viin_home_app_order field.
     *  Written immediately, not debounced: a debounce would lose the write when the user reloads
     *  within its window. On success the acknowledged csv is mirrored into state.savedOrder.
     *  Best-effort: a failed write just means the order re-reads from the server on the next open. */
    async _persistOrder(order) {
        const csv = order.join(",");
        try {
            await this.orm.write("res.users", [user.userId], { viin_home_app_order: csv });
            this.state.savedOrder = csv;
        } catch {
            // ignore: the reordered grid still shows locally until the next reload
        }
    }

    get filteredApps() {
        const query = this.state.query.trim();
        if (!query) {
            return this.apps;
        }
        return fuzzyLookup(query, this.apps, (app) => app.name);
    }

    /**
     * Every menu entry that opens an action, under its app: the pool the search box draws menu items
     * from (apps are the tiles). Read once: the menu tree does not change while this screen is up.
     */
    get menuItems() {
        if (!this._menuItems) {
            const items = [];
            const walk = (menu, trail) => {
                for (const child of menu.childrenTree || []) {
                    if (child.actionID) {
                        const path = trail.join(" / ");
                        items.push({
                            menu: child,
                            name: child.name,
                            path,
                            nameKey: normalize(child.name),
                            pathKey: normalize(`${child.name} ${path}`),
                        });
                    }
                    walk(child, [...trail, child.name]);
                }
            };
            for (const app of this.menuService.getApps()) {
                walk(this.menuService.getMenuAsTree(app.id), [app.name]);
            }
            this._menuItems = items;
        }
        return this._menuItems;
    }

    /** Menu entries (sub-menus) matching the query, found by typing so it works on touch screens. */
    get menuMatches() {
        const query = this.state.query.trim();
        if (query.length < MENU_SEARCH_MIN_LENGTH) {
            return [];
        }
        // Every typed word must appear (case- and accent-insensitively) in the entry's name or its
        // app path; the apps' letters-in-order fuzzy match would match nearly anything across a few
        // hundred entries. Entries whose own name holds all the words come first.
        const words = normalize(query).split(/\s+/).filter(Boolean);
        const hits = this.menuItems.filter((item) => words.every((w) => item.pathKey.includes(w)));
        const rank = (item) => (words.every((w) => item.nameKey.includes(w)) ? 0 : 1);
        return hits
            .map((item, index) => ({ item, index }))
            .sort((a, b) => rank(a.item) - rank(b.item) || a.index - b.index)
            .slice(0, MENU_SEARCH_MAX_RESULTS)
            .map((entry) => entry.item);
    }

    get greeting() {
        const hour = new Date().getHours();
        if (hour < 12) {
            return _t("Good morning");
        }
        if (hour < 18) {
            return _t("Good afternoon");
        }
        return _t("Good evening");
    }

    get userName() {
        return user.name;
    }

    /** Subtitle date, e.g. "Wednesday, July 16", in the user's language: luxon's default locale is
     *  the one Odoo's localization service sets from the user's lang, unlike the browser's locale. */
    get dateLabel() {
        return DateTime.now().toLocaleString({ weekday: "long", month: "long", day: "numeric" });
    }

    /** Pluralized activities label for the subtitle. */
    get activityLabel() {
        return this.activityCount === 1 ? _t("activity due today") : _t("activities due today");
    }

    getIconUrl(app) {
        return getAppIconUrl(app);
    }

    /** A tile is a real `<a href>`, so a modified click (middle, ctrl/cmd, shift, alt) is the
     *  browser's to handle. A plain primary click routes through the menu service instead of
     *  reloading the page, as core's DropdownItem does for its own app links. */
    onTileClick(ev, app) {
        if (ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) {
            return;
        }
        ev.preventDefault();
        this.launch(app);
    }

    /** Same rule as `onTileClick`, for a menu-item result. */
    onMenuItemClick(ev, menu) {
        if (ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) {
            return;
        }
        ev.preventDefault();
        this.launch(menu);
    }

    /** Open an app tile or a menu-item result: both go through the menu service. */
    launch(app) {
        if (!app) {
            return;
        }
        this.menuService.selectMenu(app);
        // The overlay would cover the app just chosen; the client-action arm is replaced by the new
        // controller instead.
        this.props.close?.();
    }

    /** Focus the search input; a no-op when it is not rendered (defensive against a mount-timing
     *  or unmount race). */
    _focusSearchInput() {
        this.searchRef.el?.focus({ preventScroll: true });
    }

    /** Move focus into the search box, unless mid-IME composition, a higher UI layer is open, an
     *  accelerator modifier is held, the key is not a single printable character, or an editable
     *  target already owns the keystroke. It never writes into the box: the browser's own keydown
     *  default delivers the character once focus has moved, so it appends instead of overwriting. */
    onWindowKeydown(ev) {
        if (ev.isComposing || ev.keyCode === 229) {
            return;
        }
        if (this.ui.activeElement !== document) {
            return;
        }
        if (ev.ctrlKey || ev.altKey || ev.metaKey) {
            return;
        }
        if (typeof ev.key !== "string" || ev.key.length !== 1) {
            return;
        }
        const target = ev.target;
        const targetIsEditable =
            target instanceof HTMLElement &&
            (/input|textarea/i.test(target.tagName) || target.isContentEditable) &&
            !target.matches("input[type=checkbox], input[type=radio]");
        if (targetIsEditable) {
            return;
        }
        this._focusSearchInput();
    }

    onSearchInput(ev) {
        this.state.query = ev.target.value;
        this.state.focusIndex = -1; // reset highlight when the result set changes
    }

    /** Number of columns actually rendered (responsive) - read from the grid's computed template. */
    _columnCount() {
        const grid = this.gridRef.el;
        if (!grid) {
            return 1;
        }
        const template = getComputedStyle(grid).gridTemplateColumns;
        return Math.max(1, template.split(" ").filter(Boolean).length);
    }

    _highlight(index) {
        const count = this.filteredApps.length;
        if (!count) {
            return;
        }
        const clamped = Math.max(0, Math.min(count - 1, index));
        this.state.focusIndex = clamped;
        // keep the highlighted tile in view without stealing focus from the search box
        this.gridRef.el
            ?.querySelector(`[data-index="${clamped}"]`)
            ?.scrollIntoView({ block: "nearest" });
    }

    onSearchKeydown(ev) {
        const cols = this._columnCount();
        const current = this.state.focusIndex;
        switch (ev.key) {
            case "ArrowRight":
                ev.preventDefault();
                this._highlight(current < 0 ? 0 : current + 1);
                break;
            case "ArrowLeft":
                ev.preventDefault();
                this._highlight(current < 0 ? 0 : current - 1);
                break;
            case "ArrowDown":
                ev.preventDefault();
                this._highlight(current < 0 ? 0 : current + cols);
                break;
            case "ArrowUp":
                ev.preventDefault();
                this._highlight(current < 0 ? 0 : current - cols);
                break;
            case "Enter": {
                ev.preventDefault();
                // An arrow-highlighted tile always opens; otherwise only a non-empty query has a
                // match to open, and an empty query with nothing highlighted opens nothing.
                if (current >= 0) {
                    this.launch(this.filteredApps[current]);
                } else if (this.state.query.trim()) {
                    // The first app match; with no app matching, the first menu-item match.
                    this.launch(this.filteredApps[0] || this.menuMatches[0]?.menu);
                }
                break;
            }
        }
    }
}

registry.category("actions").add("viin_home_menu", ViinHomeMenu);
