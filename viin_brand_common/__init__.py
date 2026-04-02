from . import controllers
from . import models

from odoo.tools import config

if config.get('test_enable', False):
    from odoo.addons.web.tests.test_webmanifest import WebManifestRoutesTest


def pass_test(self):
    """
    Because this module changes the returned data while the original tests are checking that data => pass the test and rewrite a new similar test
    """
    pass


def post_load():
    if config.get('test_enable', False):
        WebManifestRoutesTest.test_apple_touch_icon = pass_test
        WebManifestRoutesTest.test_webmanifest_unauthenticated = pass_test
        WebManifestRoutesTest.test_webmanifest = pass_test
