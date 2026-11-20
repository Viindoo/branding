import io
import os
import re
import zipfile

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open_temporary_directory

BRAND_PATTERN = re.compile(r'\bOdoo\b|odoo\.com|Enterprise', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestImportModuleBrand(TransactionCase):

    def _zip_with_missing_dependency(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('sample_data/__manifest__.py', "{'name': 'Sample', 'depends': ['not_a_known_module']}")
        return buffer.getvalue()

    def test_missing_dependencies_description_has_no_edition_or_download_offer(self):
        description, unavailable = self.env['ir.module.module']._get_missing_dependencies(
            self._zip_with_missing_dependency())
        self.assertEqual(unavailable, {'not_a_known_module'})
        self.assertIn('- not_a_known_module\n', description)
        self.assertNotRegex(description, BRAND_PATTERN)
        self.assertNotIn('github', description)

    def test_description_without_missing_dependency_is_the_core_one(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('sample_data/__manifest__.py', "{'name': 'Sample', 'depends': ['base']}")
        description, unavailable = self.env['ir.module.module']._get_missing_dependencies(buffer.getvalue())
        self.assertFalse(unavailable)
        self.assertIn('Load demo data', description)

    def test_studio_customization_error_names_no_other_product(self):
        with file_open_temporary_directory(self.env) as root:
            path = os.path.join(root, 'studio_sample')
            os.makedirs(path)
            with open(os.path.join(path, '__manifest__.py'), 'w') as manifest:
                manifest.write(
                    "{'name': 'Studio sample', 'version': '1.0', 'depends': ['base'], "
                    "'author': 'Test', 'license': 'LGPL-3'}"
                )
            with open(os.path.join(path, 'data.xml'), 'w') as data:
                data.write('<odoo><record id="r" model="ir.ui.view" context="{\'studio\': True}"/></odoo>')
            with self.assertRaises(UserError) as caught:
                self.env['ir.module.module']._import_module('studio_sample', path)
        self.assertNotRegex(caught.exception.args[0], BRAND_PATTERN)
        self.assertIn('Viindoo', caught.exception.args[0])
