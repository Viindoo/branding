import { patch } from "@web/core/utils/patch";
import { StatusBarField } from "@web/views/fields/statusbar/statusbar_field";

/**
 * Numbered steps on core's ARROW statusbar (owner request 2026-08-03: "cả 2 chế độ đều mất các số
 * step ở status bar rồi" - both schemes lost the statusbar step numbers - while explicitly keeping
 * core's chevrons: "vẫn muốn giữ cái mũi tên như mặc định").
 *
 * This is the ONLY behaviour this unit adds: a 1-based ORDINAL per step. It changes no geometry, no
 * click handling and no DOM text - statusbar_steps.xml adds a class plus a `data-viin-step`
 * attribute to the existing button and statusbar_steps.scss renders the digit as a `::after`
 * pseudo-element, so `button.textContent` is byte-identical to core's (core's own suite asserts it
 * exactly, e.g. `expect(".o_arrow_button_current").toHaveText("first record")` in
 * web/static/tests/views/fields/statusbar_field.test.js).
 *
 * WHY A GETTER AND NOT A CSS counter(). A CSS counter increments in DOM order, and the statusbar's
 * DOM order is the REVERSE of its visual order: getSortedItems() calls `inline.reverse()` and
 * statusbar_field.scss lays the row out `flex-flow: row-reverse wrap-reverse`, so the first button
 * in the DOM is the LAST stage. A counter would number the steps backwards. Nor can the template
 * count `items.inline` itself: when the bar is too narrow core folds leading/trailing steps into the
 * "..." dropdowns (adjustVisibleItems), which shrinks `items.inline` and would silently renumber the
 * remaining steps. getAllItems() is the only list that stays the whole, ordered stage sequence.
 *
 * WHY viin_brand_common AND NOT viin_backend_theme. The statusbar's chrome is this module's already:
 * it paints the current-arrow outline through core's own --o-statusbar-border-active token
 * (brand_variables.scss $o-component-active-border). The theme is under an explicit owner revert -
 * viin_backend_theme/tests/test_theme_core_chrome_untouched.py forbids it from naming
 * `o_arrow_button` / `StatusBarField` at all - so re-opening the statusbar there would mean
 * weakening that guard on the same day it was written.
 */
patch(StatusBarField.prototype, {
    /**
     * The 1-based position of `item` in the full, ordered stage sequence.
     *
     * Returns `false` (not `""`) when the item is absent, so OWL omits the attribute entirely and
     * the `::after` marker never renders an empty circle. In practice the template only ever
     * iterates items that came out of getAllItems(), so the fallback is defensive.
     *
     * @param {{ value: number|string }} item one entry of `items.inline`
     * @returns {string|false}
     */
    viinStepNumber(item) {
        const index = this.getAllItems().findIndex((candidate) => candidate.value === item.value);
        return index === -1 ? false : String(index + 1);
    },
});
