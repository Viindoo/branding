import { registries } from "@odoo/o-spreadsheet";

const { functionRegistry } = registries;

// The formulas of Odoo data (lists, pivots, currency rates, accounting) are filed under a function
// category named after the product, and the category is the label the user sees in the function
// list. A function registered after this file is re-filed as it is added.
const CORE_CATEGORY = "Odoo";
const BRAND_CATEGORY = "Viindoo";

function brandCategory(description) {
    if (description?.category === CORE_CATEGORY) {
        description.category = BRAND_CATEGORY;
    }
    return description;
}

Object.values(functionRegistry.content).forEach(brandCategory);

const add = functionRegistry.add;
functionRegistry.add = function (key, value) {
    return add.call(this, key, brandCategory(value));
};
