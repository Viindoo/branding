import io
import unittest
from unittest.mock import patch

from odoo.addons.base.tests.files import PDF_RAW
from odoo.addons.viin_brand import STOCK_BASE_ICON, get_viin_brand_module_icon
from odoo.modules import module
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import pdf


@tagged('post_install', '-at_install')
class TestCoreTestAlignment(TransactionCase):
    """The core tests of ``test_base`` that assert the Odoo branding expect Viindoo instead."""

    def _run_core_branded_writer_test(self):
        # Imported here: a test class imported at module level runs with this module.
        from odoo.addons.test_base.tests.test_tools.test_pdf import TestPdf

        self.minimal_pdf_reader = pdf.OdooPdfFileReader(io.BytesIO(PDF_RAW))
        TestPdf.test_branded_file_writer(self)

    def test_core_branded_writer_test_expects_viindoo(self):
        self._run_core_branded_writer_test()

    def test_core_branded_writer_test_fails_on_a_document_without_viindoo(self):
        class OdooWriter(pdf.PdfWriter):
            def write_stream(self, *args, **kwargs):
                self.add_metadata({'/Creator': 'Odoo', '/Producer': 'Odoo'})
                super().write_stream(*args, **kwargs)

        with patch.object(pdf, 'PdfFileWriter', OdooWriter), \
                self.assertRaises(AssertionError):
            self._run_core_branded_writer_test()

    def _core_manifest_case(self):
        from odoo.addons.test_base.tests.test_modules.test_manifest import TestModuleManifest

        return TestModuleManifest('test_default_manifest')

    def test_core_default_manifest_test_passes_with_the_viindoo_icon(self):
        from odoo.addons.test_base.tests.test_modules.test_manifest import TestModuleManifest

        result = unittest.TestResult()
        unittest.TestSuite([TestModuleManifest('test_default_manifest')]).run(result)

        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)

    def test_core_default_manifest_test_still_fails_on_any_other_difference(self):
        case = self._core_manifest_case()

        with self.assertRaises(AssertionError):
            case.assertDictEqual(
                {'icon': STOCK_BASE_ICON, 'name': 'A'}, {'icon': get_viin_brand_module_icon('base'), 'name': 'B'},
            )


@tagged('post_install', '-at_install')
class TestBrandingIsLoadedWhateverTheServerWideOrder(TransactionCase):
    """``viin_brand`` runs its ``post_load`` when this module is loaded server wide before it.

    A server-wide module that imports ``viin_brand`` at load would keep the server from running that
    hook, and the core resolver of module icons would stay the stock one.
    """

    def test_the_module_icon_resolver_of_core_is_the_viindoo_one(self):
        # the image of base under the apps folder of viin_brand, while no module viin_brand_base ships
        # its own static/description/icon.png (that one would be returned first)
        self.assertEqual(module.get_module_icon('base'), '/viin_brand/static/img/apps/base.png')
