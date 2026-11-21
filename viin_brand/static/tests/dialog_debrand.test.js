import { describe, expect, test } from "@odoo/hoot";

import { Dialog } from "@web/core/dialog/dialog";
import "@viin_brand/core/dialog/dialog";

describe.current.tags("headless");

test("backend dialog default title is de-branded to Viindoo, never Odoo", () => {
    expect(Dialog.defaultProps.title).toBe("Viindoo");
    expect(Dialog.defaultProps.title).not.toInclude("Odoo");
});
