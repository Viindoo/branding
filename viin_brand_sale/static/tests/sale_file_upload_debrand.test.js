import { animationFrame, describe, expect, test } from "@odoo/hoot";
import { queryAll, queryOne, queryText } from "@odoo/hoot-dom";
import { defineModels, fields, models, mountView } from "@web/../tests/web_test_helpers";
import { saleModels } from "@sale/../tests/sale_test_helpers";

import "@viin_brand_sale/views/sale_file_upload_kanban/sale_file_upload_kanban_renderer";
import "@viin_brand_sale/views/sale_file_upload_list/sale_file_upload_list_renderer";

class Quotation extends models.Model {
    _name = "quotation";

    name = fields.Char();

    _records = [{ id: 1, name: "S00001" }];
}

defineModels({ ...saleModels, Quotation });

describe.current.tags("desktop");

/** Drag a file over the root of a view, as a user does to import a request for quotation. */
async function dragAFileOver(selector) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(new File(["%PDF"], "request.pdf", { type: "application/pdf" }));
    queryOne(selector).dispatchEvent(
        new DragEvent("dragenter", { bubbles: true, cancelable: true, dataTransfer })
    );
    await animationFrame();
}

test("the drop zone of the kanban view of quotations names no Odoo", async () => {
    await mountView({
        type: "kanban",
        resModel: "quotation",
        arch: `<kanban js_class="sale_file_upload_kanban">
            <templates><t t-name="card"><field name="name"/></t></templates>
        </kanban>`,
    });

    await dragAFileOver(".o_kanban_renderer");

    expect(queryAll(".o_drop_area")).toHaveLength(1);
    expect(queryText(".o_drop_area")).not.toMatch(/odoo/i);
    expect(queryText(".o_drop_area span.text-center")).not.toBe("");
});

test("the drop zone of the list view of quotations names no Odoo", async () => {
    await mountView({
        type: "list",
        resModel: "quotation",
        arch: `<list js_class="sale_file_upload_list"><field name="name"/></list>`,
    });

    await dragAFileOver(".o_list_renderer");

    expect(queryAll(".o_drop_area")).toHaveLength(1);
    expect(queryText(".o_drop_area")).not.toMatch(/odoo/i);
    expect(queryText(".o_drop_area span.text-center")).not.toBe("");
});
