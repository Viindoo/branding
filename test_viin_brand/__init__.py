import functools
from unittest.mock import patch

from odoo.tools import config

# Nothing of ``viin_brand`` is imported at load: this module is loaded server wide, and an import of
# ``viin_brand`` before the server loads it would keep its ``post_load`` from running. The wrappers
# below import it when a test runs, long after every server-wide module is loaded.


def _patch_test_default_manifest_icon_expectation():
    """Realign ``TestModuleManifest`` of ``test_base`` to the Viindoo icon.

    ``test_default_manifest`` compares the manifest of a temporary module with a literal dict
    carrying the stock base icon, while the module resolves to the Viindoo base icon. The wrapper
    rewrites only an ``icon`` key equal to the stock path, so every other assertion is unchanged.
    """
    from odoo.addons.test_base.tests.test_modules.test_manifest import TestModuleManifest

    assertDictEqual_orig = TestModuleManifest.assertDictEqual

    def _rebrand_icon(mapping):
        from odoo.addons.viin_brand import STOCK_BASE_ICON, get_viin_brand_module_icon

        if isinstance(mapping, dict) and mapping.get('icon') == STOCK_BASE_ICON:
            mapping = dict(mapping, icon=get_viin_brand_module_icon('base'))
        return mapping

    def assertDictEqual(self, d1, d2, msg=None):
        return assertDictEqual_orig(self, _rebrand_icon(d1), _rebrand_icon(d2), msg)

    TestModuleManifest.assertDictEqual = assertDictEqual


def _realign_core_pdf_metadata_test():
    """Realign ``test_branded_file_writer`` of ``test_base`` to Viindoo.

    The test reads the creator and producer of a document written by ``BrandedFileWriter`` and
    compares them with ``'Odoo'``, while every written document carries Viindoo. The wrapper turns
    only that expected value into Viindoo, so the test still fails when the writer stops setting
    the entries.
    """
    from odoo.addons.test_base.tests.test_tools.test_pdf import TestPdf

    test_original = TestPdf.test_branded_file_writer

    @functools.wraps(test_original)
    def test_branded_file_writer(self):
        from odoo.addons.viin_brand.tools import PRODUCT_NAME

        assert_equal = self.assertEqual

        def assertEqual(first, second, msg=None):
            return assert_equal(first, PRODUCT_NAME if second == 'Odoo' else second, msg)

        with patch.object(self, 'assertEqual', assertEqual):
            return test_original(self)

    TestPdf.test_branded_file_writer = test_branded_file_writer


def post_load():
    if config.get('test_enable', False):
        _patch_test_default_manifest_icon_expectation()
        _realign_core_pdf_metadata_test()
