# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree, html
from psycopg2 import IntegrityError

from odoo.tests.common import HttpCase, TransactionCase, new_test_user, tagged
from odoo.tools import mute_logger

PATCH_FILES = (
    "viin_brand_mail/static/src/core/common/notification_permission_service.js",
    "viin_brand_mail/static/src/core/common/out_of_focus_service.js",
)
BRAND_DIALOG_FILES = (
    "viin_brand/static/src/core/dialog/dialog.js",
    "viin_brand/static/src/core/errors/error_dialogs.js",
    "viin_brand/static/src/core/errors/error_dialogs.xml",
)


def _bundle_paths(env, bundle):
    return [
        path.lstrip("/")
        for path, _full, _bundle, _mtime in env["ir.asset"]._get_asset_paths(
            bundle=bundle, assets_params={}
        )
    ]


@tagged("post_install", "-at_install")
class TestMailServerSideDebrand(TransactionCase):

    def test_bot_signature_is_the_bot_name(self):
        signature = self.env.ref("base.user_root").signature
        self.assertIn("ViindooBot", signature)

    def test_notification_type_constraint_names_viindoo(self):
        portal = new_test_user(self.env, login="viin_portal_notif", groups="base.group_portal")
        with self.assertRaises(IntegrityError) as caught, mute_logger("odoo.sql_db"), \
                self.cr.savepoint():
            portal.write({"notification_type": "inbox"})
            portal.flush_recordset()
        message = portal._sql_error_to_message(caught.exception)
        self.assertIn("Viindoo", message)
        self.assertNotIn("Odoo", message)

    def test_mail_server_hint_does_not_name_the_editions(self):
        combined = self.env["res.config.settings"].get_views([[False, "form"]])["views"]["form"]["arch"]
        title = etree.fromstring(combined).xpath("//setting[@id='email_servers_setting']/@title")
        self.assertTrue(title)
        self.assertEqual(title[0], title[0].strip(), "the hint carries no surrounding whitespace")
        self.assertNotRegex(title[0], r"\b(Community|Enterprise)\b")
        self.assertNotIn("Odoo", title[0])


@tagged("post_install", "-at_install")
class TestMailBundles(TransactionCase):

    def test_backend_and_public_bundles_carry_the_client_patches(self):
        for bundle in ("web.assets_backend", "mail.assets_public"):
            paths = _bundle_paths(self.env, bundle)
            for path in PATCH_FILES:
                with self.subTest(bundle=bundle, file=path):
                    self.assertIn(path, paths)

    def test_public_bundle_carries_the_dialog_and_error_files_of_viin_brand(self):
        paths = _bundle_paths(self.env, "mail.assets_public")
        for path in BRAND_DIALOG_FILES:
            with self.subTest(file=path):
                self.assertIn(path, paths)


_WAIT = """
const wait = async (predicate) => {
    for (let i = 0; i < 300; i++) {
        const value = predicate();
        if (value) { return value; }
        await new Promise((resolve) => setTimeout(resolve, 100));
    }
    throw new Error("timed out");
};
const { translationIsReady } = await wait(() => odoo.loader.modules.get("@web/core/l10n/translation"));
await translationIsReady;
"""


def _page_script(body):
    """Wrap ``body`` in the success/failure console contract of ``browser_js``."""
    return "".join((
        "(async () => {\n try {\n",
        _WAIT,
        body,
        "\n console.log('test successful');\n } catch (error) {\n",
        " console.error(error.stack || error.message || String(error));\n }\n})();\n",
    ))


@tagged("post_install", "-at_install")
class TestMailClientDebrand(HttpCase):

    def test_public_channel_page_is_titled_and_iconed_by_viindoo(self):
        channel = self.env["discuss.channel"].create({
            "name": "Public room", "channel_type": "channel", "group_public_id": False,
        })
        response = self.url_open("/discuss/channel/%d" % channel.id)
        self.assertEqual(response.status_code, 200)
        page = html.fromstring(response.content)
        self.assertEqual(page.xpath("//title")[0].text_content().strip(), "Viindoo")
        icons = page.xpath("//link[@type='image/x-icon']/@href")
        self.assertEqual(icons, ["/viin_brand/static/img/favicon.ico"])

    def _run(self, body):
        self.browser_js("/odoo", _page_script(body), login="admin", timeout=120)

    def test_permission_toasts_name_viindoo(self):
        self._run("""
            const { notificationPermissionService } = await wait(
                () => odoo.loader.modules.get("@mail/core/common/notification_permission_service")
            );
            const { browser } = odoo.loader.modules.get("@web/core/browser/browser");
            const seen = [];
            const notification = { add: (message) => seen.push(String(message)) };
            const stubbed = { query: async () => ({ state: "prompt", addEventListener() {} }) };
            Object.defineProperty(navigator, "permissions", { value: stubbed, configurable: true });
            browser.Notification = { permission: "default", requestPermission: async () => "denied" };
            let state = await notificationPermissionService.start({}, { notification });
            await state.requestPermission();
            browser.Notification = { permission: "default", requestPermission: async () => "granted" };
            state = await notificationPermissionService.start({}, { notification });
            await state.requestPermission();
            const wrong = (text) => text.includes("Odoo") || !text.includes("Viindoo");
            if (seen.length !== 2 || seen.some(wrong)) {
                throw new Error("permission toasts read: " + JSON.stringify(seen));
            }
        """)

    def test_desktop_notification_icon_is_the_viindoo_bot(self):
        self._run("""
            const { OutOfFocusService } = await wait(
                () => odoo.loader.modules.get("@mail/core/common/out_of_focus_service")
            );
            const icons = [];
            const OriginalNotification = window.Notification;
            window.Notification = class {
                constructor(title, options) { icons.push(options.icon); }
                addEventListener() {}
            };
            const send = (icon) => OutOfFocusService.prototype.sendNativeNotification.call(
                { _playSound() {} }, "t", "m", icon, { sound: false }
            );
            try {
                send("/mail/static/src/img/odoobot_transparent.webp");
                send("/author.png");
            } finally {
                window.Notification = OriginalNotification;
            }
            if (icons[0] !== "/viin_brand/static/img/viindoobot.png" || icons[1] !== "/author.png") {
                throw new Error("notification icons: " + JSON.stringify(icons));
            }
        """)
