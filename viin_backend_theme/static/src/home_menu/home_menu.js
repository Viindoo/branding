/** @odoo-module **/

// D3 - ViinHomeMenu: full-page flat "Applications" grid client action (tag "viin_home_menu").
// ONE flat dense grid (no category sections, no sticky headers). Search-first: filters with the core
// fuzzyLookup (NOT Fuse.js). Keyboard: arrow keys move a highlight across the responsive grid and
// Enter launches the highlighted app. Icons load lazily so 100+ PNGs don't block first paint. Reads
// the native menuService app list and launches via menuService.selectMenu.
//
// PR #658 item 7 - per-user drag-reorder: the grid is ordered by the user's stored
// res.users.viin_home_app_order (app root-menu xmlids); a press-drag reorders the tiles and persists
// the new order to that SELF_WRITEABLE field. Apps missing from the stored order (newly installed)
// append at the end in default sequence and are never hidden - the feature is purely additive to the
// keyboard/click paths above.
//
// SEARCH-FIRST FOCUS: `onMounted` pre-focuses ViinHomeMenu's search box on mount, in both render
// shapes, whenever `hasTouch` reports no touch support - a deliberate product decision: land on the
// screen, type, and searching starts immediately, with no click first. Recovering a keystroke that
// arrives once focus has moved elsewhere (`onWindowKeydown`) needs the box to already hold focus so
// a composition-based IME session can attach to it and so the browser's native keydown appends
// rather than overwrites - guarded by `static/tests/viin_home_typeahead.test.js`.
//
// COST, ACCEPTED: pre-focusing the search box means it, not the shell's `.o_viin_skip_link`
// bypass-blocks link (WCAG 2.4.1), receives the page's very first Tab. The skip link stays present,
// reachable by Shift-Tab from the search box or by landmark/heading screen-reader navigation, and
// activating it still moves focus into the main action region (`skipToMainContent`,
// webclient_patch.js) - only its place as the FIRST stop is given up, on purpose, for the
// search-first goal above. The search input's `aria-label` (home_menu.xml) covers the resulting
// gap: a screen-reader user landing there on mount is told what the field is, not left with no
// orientation at all. `data-allow-hotkeys="true"` (home_menu.xml) keeps core's global hotkeys
// reachable while the box holds focus by default (`@web/core/hotkeys/hotkey_service.js`
// `shouldProtectEditable`). `role="combobox"` was evaluated and rejected: it implies
// `aria-expanded`/`aria-controls`/`aria-activedescendant` wiring a popup listbox this markup does
// not have - the grid is always visible, never a popup - so the implicit textbox role plus the
// `aria-label` describes this input correctly and a bare `role="combobox"` would not.
//
// D3 MECHANISM CHANGE, 2026-08-17 (owner decision D3) - THIS COMPONENT NOW HAS TWO MOUNT POINTS.
// It used to be reachable ONLY as a full-page client action, which meant the navbar apps button had
// to `doAction()` - and a doAction UNMOUNTS the controller the user was on. Core's contract for that
// button is the opposite: `.o_navbar_apps_menu button` opens a popover and does NOT navigate, which
// is what all 57 core tour files built on `stepUtils.showAppsMenuItem()` depend on (they either open
// an app from the list that appears, or click the button as harmless boilerplate and keep working on
// the SAME view). So the navbar arm now renders this component through the OVERLAY service instead,
// above the still-mounted controller, and the client action survives for the BOOT LANDING only -
// where there is no controller to preserve. ONE button, ONE home menu, one design; only the
// mechanism differs, and the user cannot tell the two apart.
//
// The tiles are `<a href>` rather than `<button>` for the same reason core renders its own app list
// that way (dropdown_item.xml picks the tag from the presence of `href`): middle-click opens a new
// tab, right-click copies the link, and a screen reader announces a link to a page. Nothing about
// the rendered tile changes.

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
import { useService } from "@web/core/utils/hooks";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { useSortable } from "@web/core/utils/sortable_owl";
import { fuzzyLookup } from "@web/core/utils/search";
import { _t } from "@web/core/l10n/translation";
import { user } from "@web/core/user";
import { NavBar } from "@web/webclient/navbar/navbar";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { getAppIconUrl } from "../webclient/app_icons";

// The navbar chrome the OVERLAY arm must not treat as "outside" - clicking the apps button is the
// toggle, and it must reach its own handler with the overlay still open (a pointerdown-close here
// would close it a beat before the click re-opened it, i.e. the toggle would never shut).
const APPS_MENU_SELECTOR = ".o_navbar_apps_menu";
const OVERLAY_ROOT_SELECTOR = ".o_viin_home_overlay";

export class ViinHomeMenu extends Component {
    static template = "viin_backend_theme.ViinHomeMenu";
    // TWO MOUNT POINTS, ONE COMPONENT (D3 mechanism change, 2026-08-17). This renders either as the
    // BOOT-LANDING client action (WebClient._loadDefaultApp - the action-service props below), or as
    // the NON-NAVIGATING OVERLAY the navbar apps button opens (`close` set, no action). `action` is
    // therefore optional: the overlay arm has no action behind it, which is the entire point - the
    // controller the user was on stays mounted underneath.
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
        // Pre-focus the search box the moment this component mounts, in EITHER render shape - see
        // the file header for the full WCAG/IME reasoning. Skipped on a touch device: an
        // unrequested virtual keyboard popping on a screen the user has not touched yet is worse
        // than leaving it unfocused.
        onMounted(() => {
            if (!hasTouch()) {
                this._focusSearchInput();
            }
        });
        // Type-to-search RECOVERY: a printable keystroke with nothing editable focused must move
        // focus back into the search box, in EITHER render shape, so this is unconditional rather
        // than gated on isOverlay - the FIRST keystroke on mount is already covered by the pre-focus
        // above; this listener only recovers focus after it was lost. useHotkey cannot express "any
        // printable character" - core's AUTHORIZED_KEYS (hotkey_service.js) excludes most printable
        // punctuation - so this listens directly and mirrors that same file's IME-composition check,
        // its targetIsEditable/shouldProtectEditable rule (an already-focused editable, including
        // the search box itself, keeps its own native typing untouched), and its `ui.activeElement`
        // UI-layering check (a Dialog or other higher layer owns the keystroke instead).
        useExternalListener(window, "keydown", this.onWindowKeydown);
        if (this.isOverlay) {
            // DISMISSAL, borrowed verbatim from what core's own apps DROPDOWN does - because the
            // contract this overlay restores is core's: clicking the apps button must not navigate,
            // and interacting with the page underneath must put the app list away again
            // (web/static/src/core/dropdown/dropdown.js `closeOnClickAway`, no backdrop). A pointer
            // interaction that lands outside both the overlay and the navbar apps button closes it.
            // In a real session that is a click on the navbar; under a tour it is the next step's
            // click on the controller below, which is exactly the behaviour that leaves the DOM
            // clean for the rest of the tour instead of stranding a full-screen panel over it.
            useExternalListener(document, "pointerdown", this.onOutsidePointerDown, {
                capture: true,
            });
            // Escape dismisses and hands focus back to the button that opened it - a non-modal
            // overlay that traps the user is an accessibility defect (WCAG 2.1.2). The full-page
            // client-action arm has no trigger to return to, so it does not register this.
            useHotkey("escape", () => this.props.close({ restoreFocus: true }), {
                bypassEditableProtection: true,
            });
        }
        this.state = useState({
            query: "",
            // index of the highlighted tile within `filteredApps` (arrow-nav), -1 = none
            focusIndex: -1,
            // per-user tile order (app root-menu xmlids); [] = default menu sequence. Read from
            // res.users.viin_home_app_order in onWillStart, then rewritten reactively on each drop.
            appOrder: [],
            // csv of the LAST order the server has ACKNOWLEDGED (set after the ORM write resolves).
            // Surfaced on the grid as data-viin-saved-order so a caller can tell when a drop has
            // persisted server-side (used by the persist tour before it reloads).
            savedOrder: null,
        });
        // Press-drag a tile to reorder the grid (an enhancement - keyboard arrow-nav + click still
        // work). A movement TOLERANCE (not a press-delay) discriminates a plain tap (launches the app,
        // no move) from a deliberate press-drag (reorders): a real drag sets the sortable's
        // preventClick, so the dragged tile never launches on drop. Disabled while searching, since the
        // filtered/score-ordered subset is not the persisted order. Grounded on core list_renderer /
        // kanban_renderer / control_panel, which use the same tolerance-based discrimination when one
        // element is both the click and the drag target.
        useSortable({
            enable: () => !this.state.query,
            ref: this.gridRef,
            elements: ".o_viin_home_app",
            cursor: "move",
            tolerance: 10,
            onDrop: (params) => this.onTileDrop(params),
        });
        // Mockup header subtitle: "<date> · N activities due today" plus the stored app order - read
        // together in one onWillStart. Each read degrades on its own (a failure never blanks the grid):
        // activities due today-or-earlier (Odoo's "today" activity meaning includes overdue) default to
        // 0, the app order defaults to the empty (default-sequence) list.
        this.activityCount = 0;
        onWillStart(async () => {
            // Local date in ISO form (YYYY-MM-DD) for the server domain; "en-CA" yields ISO order from
            // the LOCAL date (not UTC), avoiding a midnight off-by-one.
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
        if (target.closest(OVERLAY_ROOT_SELECTOR) || target.closest(APPS_MENU_SELECTOR)) {
            return;
        }
        this.props.close();
    }

    /** The tile's `href`, from CORE's OWN helper - never a second copy of the URL scheme.
     *
     *  `NavBar.prototype.getMenuItemHref` is the single place Odoo 19 builds an app's backend URL
     *  (`/odoo/<actionPath|action-<id>>`, navbar.js), and it is what core's own apps-menu
     *  DropdownItems are given. It reads nothing off `this`, so calling it through the prototype is
     *  safe and keeps ONE definition: if core changes the URL shape, these tiles follow it for free
     *  instead of silently pointing at a dead route. */
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

    /** Order apps by the per-user preference (state.appOrder): apps whose root-menu xmlid appears in
     *  the stored order come first, in that order; apps NOT in it (newly installed / never dragged)
     *  keep the default menu sequence and append at the END. Never filters - every accessible app
     *  always renders, so a stale stored value can never hide an app. */
    _orderApps(apps) {
        const rank = new Map(this.state.appOrder.map((xmlid, index) => [xmlid, index]));
        return apps
            .map((app, index) => ({ app, index }))
            .sort((a, b) => {
                const ra = rank.has(a.app.xmlid) ? rank.get(a.app.xmlid) : Infinity;
                const rb = rank.has(b.app.xmlid) ? rank.get(b.app.xmlid) : Infinity;
                // Equal rank (both unknown): keep the default menu sequence (stable by original index).
                return ra === rb ? a.index - b.index : ra - rb;
            })
            .map((entry) => entry.app);
    }

    /** On drop, splice the dragged tile to its new slot (after `previous`, or first if none), rewrite
     *  the reactive order so the grid re-renders in the new order, then persist it. Mirrors the
     *  canonical core reorder algorithm (control_panel.js _sortEmbeddedActionDrop). */
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

    /** Persist the reordered app list to the current user's SELF_WRITEABLE viin_home_app_order field.
     *  Written IMMEDIATELY (not debounced): a drop is a discrete, deliberate action, and a debounce
     *  would silently drop the write when the user reorders then navigates/reloads within the debounce
     *  window. On success the acknowledged csv is mirrored into state.savedOrder (surfaced on the grid
     *  as data-viin-saved-order) so a caller can tell the write has landed server-side. Best-effort:
     *  a failed write just means the order re-reads from the server on the next open. */
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

    /** Mockup subtitle date, e.g. "Wednesday, July 16" - locale-aware via the native Intl date API. */
    get dateLabel() {
        return new Date().toLocaleDateString(undefined, {
            weekday: "long",
            month: "long",
            day: "numeric",
        });
    }

    /** Pluralized activities label for the subtitle. */
    get activityLabel() {
        return this.activityCount === 1 ? _t("activity due today") : _t("activities due today");
    }

    getIconUrl(app) {
        return getAppIconUrl(app);
    }

    /** A tile is a real `<a href>`, so a MODIFIED click is the browser's to handle - that is the
     *  whole reason it is a link and not a button: middle-click and ctrl/cmd-click open the app in a
     *  new tab, shift-click in a new window, and right-click offers "copy link address". A plain
     *  primary click is ours: the webclient is a single-page app, so it routes through the menu
     *  service instead of reloading the page. Core's DropdownItem takes the same preventDefault
     *  branch on its own app links (dropdown_item.js `onClick`). */
    onTileClick(ev, app) {
        if (ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) {
            return;
        }
        ev.preventDefault();
        this.launch(app);
    }

    launch(app) {
        if (!app) {
            return;
        }
        this.menuService.selectMenu(app);
        // The overlay's job is done the moment an app is chosen; leaving it up would cover the app
        // the user just asked for. (The client-action arm is replaced by the new controller instead.)
        this.props.close?.();
    }

    /** Focus the search input; a no-op when it is not rendered (defensive against a mount-timing
     *  or unmount race). */
    _focusSearchInput() {
        this.searchRef.el?.focus({ preventScroll: true });
    }

    /** Move focus into the search box, unless a guard says otherwise: mid-IME composition, a
     *  higher UI layer open, an accelerator modifier held, not a single printable character, or an
     *  editable target already owns the keystroke. Reads `ev.key` only to check that guard; it
     *  never WRITES into the search box - no `input.value` assignment, no injecting `ev.key` -
     *  so the browser's own keydown default action delivers the character natively once focus has
     *  moved, which is what makes a recovered keystroke APPEND to content already in the box
     *  instead of overwriting it. */
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
                // An explicit arrow-highlight always wins, typed or not (rule: highlighted tile
                // opens regardless of query). Otherwise, only a non-empty query has a match worth
                // opening (rule: type-then-Enter opens the first match); an empty query with
                // nothing highlighted opens nothing (rule: no selection, no launch).
                if (current >= 0) {
                    this.launch(this.filteredApps[current]);
                } else if (this.state.query.trim()) {
                    this.launch(this.filteredApps[0]);
                }
                break;
            }
        }
    }
}

registry.category("actions").add("viin_home_menu", ViinHomeMenu);
