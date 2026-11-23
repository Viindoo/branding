import { registries } from "@odoo/o-spreadsheet";

const { functionRegistry } = registries;

// The formulas of Odoo data (lists, pivots, currency rates, accounting) are filed under a function
// category named after the product, and the category is the label the user sees in the function
// list. A function registered after this file is re-filed as it is added. The description is a
// lazily translated text that is read when the help of the function is shown, so it is re-worded
// when it is read.
const CORE_CATEGORY = "Odoo";
const BRAND_CATEGORY = "Viindoo";

function brandFunction(description) {
    if (description?.category === CORE_CATEGORY) {
        description.category = BRAND_CATEGORY;
        const text = description.description;
        if (text) {
            Object.defineProperty(description, "description", {
                get: () => String(text).replaceAll("Odoo", "Viindoo"),
                configurable: true,
                enumerable: true,
            });
        }
    }
    return description;
}

Object.values(functionRegistry.content).forEach(brandFunction);

const add = functionRegistry.add;
functionRegistry.add = function (key, value) {
    return add.call(this, key, brandFunction(value));
};
