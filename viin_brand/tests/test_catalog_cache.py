import os
import tempfile
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.models import ir_module_module

PO_HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
# The most parsed catalogs the cache may keep: the few hundred files of the branding catalogs fit under it.
MAX_SENSIBLE_BOUND = 1024
ENTRY = '#. module: base\n#: model:ir.actions.act_window,help:base.action_partner_form\nmsgid "%s"\nmsgstr ""\n'


@tagged('post_install', '-at_install')
class TestCatalogCache(TransactionCase):
    """The catalogs a language load reads are parsed once, and read again when the file changes."""

    def _write(self, path, source):
        with open(path, 'w', encoding='utf-8') as po_file:
            po_file.write(PO_HEADER + ENTRY % source)

    def _sources(self, path):
        # the catalog is read from a folder outside the addons paths
        with patch.object(ir_module_module, 'file_open', lambda name, mode: open(name, mode)):
            index = self.env['ir.module.module']._read_catalog(path)
        return {source for rows in index.values() for _key, source, _value in rows}

    def test_a_catalog_edited_and_given_back_its_modification_time_is_read_again(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'catalog.po')
            self._write(path, 'First')
            before = os.stat(path)
            self.assertEqual(self._sources(path), {'First'})
            self._write(path, 'Second')
            os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
            self.assertEqual(self._sources(path), {'Second'})

    def test_a_catalog_edited_to_the_same_size_with_a_new_modification_time_is_read_again(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'catalog.po')
            self._write(path, 'First')
            before = os.stat(path)
            self.assertEqual(self._sources(path), {'First'})
            self._write(path, 'Third')
            os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
            self.assertEqual(self._sources(path), {'Third'})

    def test_the_parsed_catalogs_are_kept_up_to_a_bound(self):
        bound = ir_module_module._parse_catalog.cache_info().maxsize
        self.assertIsNotNone(bound)
        self.assertLessEqual(bound, MAX_SENSIBLE_BOUND)
        ir_module_module._parse_catalog.cache_clear()
        with tempfile.TemporaryDirectory() as folder:
            paths = [os.path.join(folder, 'catalog_%d.po' % number) for number in range(bound + 1)]
            for number, path in enumerate(paths):
                self._write(path, 'Source %d' % number)
                self._sources(path)
            self.assertEqual(ir_module_module._parse_catalog.cache_info().currsize, bound)
            self.assertEqual(self._sources(paths[0]), {'Source 0'})
