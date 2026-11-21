import { DocumentSelector } from "@html_editor/main/media/media_dialog/document_selector";
import { ImageSelector } from "@html_editor/main/media/media_dialog/image_selector";
import { patch } from "@web/core/utils/patch";

export const IMAGE_URL_PLACEHOLDER = "https://www.example.com/logo.png";
export const DOCUMENT_URL_PLACEHOLDER = "https://www.example.com/mydocument";

patch(ImageSelector.prototype, {
    setup() {
        super.setup(...arguments);
        this.urlPlaceholder = IMAGE_URL_PLACEHOLDER;
    },
});

patch(DocumentSelector.prototype, {
    setup() {
        super.setup(...arguments);
        this.urlPlaceholder = DOCUMENT_URL_PLACEHOLDER;
    },
});
