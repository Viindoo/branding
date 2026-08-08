import {
    defineLivechatModels,
    loadDefaultEmbedConfig,
} from "@im_livechat/../tests/livechat_test_helpers";
import { contains, start, startServer } from "@mail/../tests/mail_test_helpers";
import { describe, test } from "@odoo/hoot";

// Business rule under protection: the livechat launcher button must actually appear on every
// frontend page, unconditionally - it is the ONLY entry point a website visitor has into live
// chat. viin_brand_im_livechat overrides core's im_livechat.LivechatButton QWeb template
// (static/src/embed/common/livechat_button.xml) to inject `top: {{ position.top }}`,
// `left: {{ position.left }}` and `width/height: {{size}}px` into the button's t-attf-style.
// Core's LivechatButton component (im_livechat/static/src/embed/common/livechat_button.js:6-45)
// defines only `this.store`, `this.livechatService`, `this.state` and `this.ref` - there is no
// `position` and no `size` anywhere on the component or its rendering context. Evaluating
// `position.top` against `undefined` throws `TypeError: Cannot read properties of undefined
// (reading 'top')` inside Owl's QWeb render, which aborts the render of the button's whole
// subtree - the launcher never appears on ANY page (live-reproduced on `/` and `/forum/help-1`,
// acceptance report BUG S39-1). This is a CRITICAL site-wide functional break: it silently
// removes the chat entry point for every visitor, on every install of this module.
//
// The override's only OTHER effect - a hardcoded `background-color: #00bbce` - is not actually
// this module's real branding mechanism for the button colour; that already happens through
// `viin_brand_im_livechat/models/im_livechat_channel.py`, which changes the
// `im_livechat.channel.button_background_color` field DEFAULT from core's Odoo-purple
// `#875A7B` to Viindoo's `#7f4282` - a value core's OWN, unmodified template already renders via
// `{{livechatService.options.button_background_color}}`
// (im_livechat/static/src/embed/common/livechat_button.xml:9). So the button can render
// correctly branded through the model default alone, with no JS/XML override needed at all.
//
// Mounted exactly like core's own embed suite (im_livechat/static/tests/embed/
// livechat_button.test.js, test "open/close temporary channel"): `loadDefaultEmbedConfig()` seeds
// a channel_id and marks livechat available, `start({ authenticateAs: false })` boots the embed
// WebClient as a fresh guest - the same path that mounts LivechatButton as a ChatHub child on
// every real frontend page (im_livechat/static/src/embed/common/chat_hub_patch.js patches
// ChatHub.components to add LivechatButton once im_livechat.assets_embed_core loads). This test's
// own bundle (im_livechat.embed_assets_unit_tests, wired in this module's manifest) transitively
// loads im_livechat.assets_embed_core - the SAME bundle viin_brand_im_livechat's override file is
// wired into - so the buggy override is ACTIVE for this test exactly as it is on a live site;
// mounting the component in isolation with a hand-rolled env would NOT reproduce that.
//
// RED-before-green: against the current worktree (override file present - a HARD CONSTRAINT of
// this authoring round forbids modifying it here), `isShown` is true immediately after
// `loadDefaultEmbedConfig()` + `start({ authenticateAs: false })` - the identical precondition
// core's own passing "open/close temporary channel" test relies on - so the button template
// renders and throws. Hoot's runner listens for `window` "error"/"unhandledrejection" globally
// (web/static/lib/hoot/core/runner.js:469-470) and fails the running test on either, so the
// uncaught TypeError alone fails this test; the `contains(".o-livechat-LivechatButton")`
// assertion below additionally proves the concrete user-visible symptom - the launcher button
// never reaches the DOM. Once the crashing override file is deleted (the planned fix),
// LivechatButton renders via core's unmodified template only and both failure modes clear.
describe.current.tags("desktop");
defineLivechatModels();

test("the livechat launcher button must render without throwing, even with the module's own style override active", async () => {
    await startServer();
    await loadDefaultEmbedConfig();
    await start({ authenticateAs: false });
    // A crash inside Owl's render aborts the button's whole subtree, so this is both the
    // functional assertion (the visitor's only chat entry point must exist) and, since `contains`
    // polls until timeout before failing, proof that no later re-render recovers it either.
    await contains(".o-livechat-LivechatButton");
});
