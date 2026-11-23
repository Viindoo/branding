import re

from odoo.tests.common import TransactionCase, tagged

BUNDLE = 'mrp_subcontracting.webclient'
CORE_FILE = 'web/static/src/core/dialog/dialog.js'
BRAND_FILES = [
    'viin_brand/static/src/core/dialog/dialog.js',
    'viin_brand/static/src/webclient/actions/action_dialog.js',
    'viin_brand/static/src/core/errors/error_dialogs.js',
    'viin_brand/static/src/core/errors/error_dialogs.xml',
    'viin_brand/static/src/core/errors/error_notifications.js',
    'viin_brand/static/src/core/barcode/barcode_video_scanner.js',
    'viin_brand/static/src/webclient/actions/reports/report_notification.js',
]


@tagged('post_install', '-at_install')
class TestSubcontractingPortalBundle(TransactionCase):

    def test_portal_bundle_lists_the_brand_files_after_the_core_ones(self):
        paths = [
            path.lstrip('/')
            for path, _full, _bundle, _mtime in self.env['ir.asset']._get_asset_paths(bundle=BUNDLE, assets_params={})
        ]
        self.assertIn(CORE_FILE, paths)
        for brand_file in BRAND_FILES:
            with self.subTest(file=brand_file):
                self.assertIn(brand_file, paths)
                self.assertGreater(paths.index(brand_file), paths.index(CORE_FILE))

    def test_portal_bundle_builds_with_every_brand_file_resolved(self):
        bundle = self.env['ir.qweb']._get_asset_bundle(BUNDLE, css=False, js=True)
        js = (bundle.js().raw or b'').decode('utf-8', 'replace')
        swallowed = re.compile(r'(?:console\.error|throw new Error)\("(?:[^"\\]|\\.)*"\)')
        own_errors = [call for call in swallowed.findall(js) if 'viin_brand/' in call]
        self.assertFalse(own_errors, own_errors)
        for brand_file in BRAND_FILES:
            with self.subTest(file=brand_file):
                self.assertIn(brand_file, js)
