import {
    defineLivechatModels,
    loadDefaultEmbedConfig,
} from "@im_livechat/../tests/livechat_test_helpers";
import { contains, start, startServer } from "@mail/../tests/mail_test_helpers";
import { describe, test } from "@odoo/hoot";

// The livechat launcher button is a website visitor's only entry point into live chat, so it must
// render on every frontend page. This test boots the embed WebClient as a guest, with this
// module's embed assets loaded through im_livechat.embed_assets_unit_tests. A template override
// reading properties LivechatButton does not define would abort the render of the whole button.
describe.current.tags("desktop");
defineLivechatModels();

test("the livechat launcher button renders without throwing with the module's embed assets loaded", async () => {
    await startServer();
    await loadDefaultEmbedConfig();
    await start({ authenticateAs: false, waitUntilSubscribe: false });
    // `contains` polls until timeout, so a later re-render cannot recover a crashed render.
    await contains(".o-livechat-LivechatButton");
});
