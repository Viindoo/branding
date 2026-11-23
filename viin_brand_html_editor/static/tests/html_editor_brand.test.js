import { ImageCrop } from "@html_editor/main/media/image_crop";
import { describe, expect, test } from "@odoo/hoot";
import { click, waitFor } from "@odoo/hoot-dom";
import { animationFrame } from "@odoo/hoot-mock";
import { mountWithCleanup, onRpc } from "@web/../tests/web_test_helpers";
import { getTemplate } from "@web/core/templates";
import "@viin_brand_html_editor/main/image_crop_brand";
import "@viin_brand_html_editor/main/media_dialog_brand";
import { setupEditor } from "@html_editor/../tests/_helpers/editor";

describe.current.tags("headless");

const BRAND_NAME = /\bOdoo\b|odoo\.com/i;

test("the link popover URL placeholder suggests a neutral address", () => {
    const input = getTemplate("html_editor.linkPopover").querySelector(
        "input[name='o_linkpopover_url']"
    );
    expect(input.getAttribute("placeholder")).not.toMatch(BRAND_NAME);
    expect(input.getAttribute("placeholder")).toInclude("example.com");
});

test("the media dialog URL placeholders suggest neutral addresses", async () => {
    onRpc("ir.attachment", "search_read", () => []);
    await setupEditor(`<p><img class="img-fluid" src="/web/static/img/logo.png"></p>`);
    await click("img");
    await waitFor(".o-we-toolbar");
    await click("button[name='replace_image']");
    await animationFrame();
    await waitFor(".o_upload_media_url_button");
    await click(".o_upload_media_url_button");
    await waitFor("input[name='url']");
    expect("input[name='url']").not.toHaveAttribute("placeholder", BRAND_NAME);
    expect("input[name='url']").toHaveAttribute("placeholder", /example\.com/);
    await click(".nav-link:contains('Documents')");
    await animationFrame();
    await click(".o_upload_media_url_button");
    await waitFor("input[name='url']");
    expect("input[name='url']").not.toHaveAttribute("placeholder", BRAND_NAME);
    expect("input[name='url']").toHaveAttribute("placeholder", /example\.com/);
});

test("the notification of an image that cannot be cropped names Viindoo", async () => {
    onRpc("/html_editor/get_image_info", () => ({}));
    const media = document.createElement("img");
    media.setAttribute("src", "https://example.com/external.png");
    document.body.append(media);
    await mountWithCleanup(ImageCrop, { props: { document, media } });
    await waitFor(".o_notification_content");
    expect(".o_notification_content").not.toHaveText(BRAND_NAME);
    expect(".o_notification_content").toHaveText(/Viindoo/);
});
