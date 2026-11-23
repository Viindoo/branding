import { ImageCrop } from "@html_editor/main/media/image_crop";
import { markup } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(ImageCrop.prototype, {
    setup() {
        super.setup(...arguments);
        const notification = this.notification;
        // ImageCrop only calls notification.add, with a message that names the product.
        this.notification = {
            add: (message, options) => {
                const text = message?.toString().replace(/\bOdoo\b/g, "Viindoo");
                return notification.add(typeof message === "string" ? text : markup(text), options);
            },
        };
    },
});
