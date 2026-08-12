# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from . import controllers
from . import models

from odoo.tools import config

if config.get('test_enable', False):
    try:
        from odoo.addons.web.tests.test_webmanifest import WebManifestRoutesTest
    except ImportError:
        WebManifestRoutesTest = None


def pass_test(self):
    """
    This module rebrands the manifest data that the core WebManifestRoutesTest asserts against Odoo
    branding (name 'Odoo', colour #714B67, odoo icons). Neuter exactly the core methods whose
    assertions our overrides invalidate; viin_brand_web's own BrandWebManifestRoutesTest re-asserts
    the equivalent Viindoo behaviour. Methods we do NOT override (test_serviceworker,
    test_offline_url) keep running unchanged.
    """
    pass


def post_load():
    if config.get('test_enable', False) and WebManifestRoutesTest:
        WebManifestRoutesTest.test_apple_touch_icon = pass_test
        WebManifestRoutesTest.test_webmanifest_unauthenticated = pass_test
        WebManifestRoutesTest.test_webmanifest = pass_test
        WebManifestRoutesTest.test_webmanifest_scoped = pass_test
