import { patch } from "@web/core/utils/patch";
import { StatusBarField } from "@web/views/fields/statusbar/statusbar_field";

/**
 * Numbered steps on core's arrow statusbar: a 1-based ordinal per step. Geometry, click handling
 * and DOM text are unchanged (statusbar_steps.xml adds a class and a `data-viin-step` attribute,
 * statusbar_steps.scss renders the digit as a `::after`), so `button.textContent` equals core's.
 *
 * The ordinal comes from a getter, not a CSS counter: the DOM order is the reverse of the visual
 * order (getSortedItems() reverses `inline`, and the row is laid out `row-reverse`), and
 * `items.inline` shrinks when the bar folds steps into the "..." dropdowns. getAllItems() is the
 * only list that stays the whole, ordered stage sequence.
 */
patch(StatusBarField.prototype, {
    /**
     * The 1-based position of `item` in the full, ordered stage sequence.
     *
     * Returns `false` (not `""`) when the item is absent, so OWL omits the attribute and the
     * `::after` marker never renders an empty circle.
     *
     * @param {{ value: number|string }} item one entry of `items.inline`
     * @returns {string|false}
     */
    viinStepNumber(item) {
        const index = this.getAllItems().findIndex((candidate) => candidate.value === item.value);
        return index === -1 ? false : String(index + 1);
    },
});
