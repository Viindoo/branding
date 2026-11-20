import functools
import logging
import os
from urllib.parse import urlparse

from odoo.modules import module
from odoo.modules.module import Manifest, get_module_path
from odoo.tools import config

from odoo.addons.base.models.ir_ui_menu import IrUiMenu

# imported here to avoid dependency cycle issues
# pylint: disable=wrong-import-position
from . import controllers
from . import models
from .apriori import modules_website
from .models.ir_module_module import IAP_SERVICE_MODULES

_logger = logging.getLogger(__name__)

get_module_icon = module.get_module_icon
_load_manifest_orig = module._load_manifest
_compute_web_icon_data = IrUiMenu._compute_web_icon_data

STOCK_BASE_ICON = '/base/static/description/icon.png'

if 'viin_brand' not in config.options.get('server_wide_modules', []):
    _logger.warning("The module `viin_brand` should be loaded in server wide mode using `--load`"
                    " option when starting Odoo server (e.g. --load=base,web,viin_brand)."
                    " Otherwise, module icons and the favicon are only branded after an update.")


def _is_installable(module_name):
    manifest = Manifest.for_addon(module_name, display_warning=False)
    return bool(manifest and manifest['installable'])


def check_viin_brand_module_icon(module_name):
    """Find the Viindoo icon of a module.

    The icon is either ``/viin_brand_<module>/static/description/icon.png`` or
    ``/viin_brand/static/img/apps/<module>.png``.

    :param module_name: technical name of the module whose icon is looked up
    :return: the icon path, or ``False`` when no Viindoo icon exists
    """
    brand_module_name = 'viin_brand_%s' % (
        module_name if module_name not in ('general_settings', 'modules') else 'base')
    brand_module_path = get_module_path(brand_module_name, display_warning=False)
    if brand_module_path and _is_installable(brand_module_name):
        brand_icon = os.path.join('static', 'description', 'icon.png')
        if os.path.exists(os.path.join(brand_module_path, brand_icon)):
            return os.path.join('/', brand_module_name, brand_icon)

    icon_name = {'general_settings': 'settings'}.get(module_name, module_name)
    icon_path = os.path.join('static', 'img', 'apps', '%s.png' % icon_name)
    if os.path.exists(os.path.join(get_module_path('viin_brand', display_warning=False), icon_path)):
        return os.path.join('/', 'viin_brand', icon_path)
    return False


def get_viin_brand_module_icon(mod):
    """Replace ``odoo.modules.module.get_module_icon`` with the Viindoo icon of a module.

    The de-brand applies in every mode, including ``--test-enable``; the core tests that hardcode
    the stock icon are realigned by ``viin_brand_mail``. A module whose icon is the stock base
    icon gets the Viindoo base icon.

    :param mod: technical name of the module
    :return: the icon path
    """
    module_icon = check_viin_brand_module_icon(mod)
    if mod not in ('general_settings', 'modules', 'settings', 'missing'):
        if get_module_icon(mod) == STOCK_BASE_ICON:
            module_icon = check_viin_brand_module_icon('base')
    return module_icon or get_module_icon(mod)


def _is_odoo_website(url):
    hostname = urlparse(url or '').hostname or ''
    return hostname == 'odoo.com' or hostname.endswith('.odoo.com')


def _load_manifest_plus(module_name, manifest_content):
    """Replace ``odoo.modules.module._load_manifest`` to brand the manifest of a module.

    Every manifest creation path goes through ``_load_manifest``, so the manifest is branded
    however it is read:

    * the ``website`` of a module listed in ``apriori.modules_website`` is its Viindoo page, and the
      ``website`` of any other module that points at odoo.com is emptied, so Apps shows no
      "Learn more" button to Odoo;
    * the modules that sell Odoo IAP credits are not installed automatically.
    """
    info = _load_manifest_orig(module_name, manifest_content)
    if module_name in modules_website:
        info['website'] = modules_website[module_name]
    elif _is_odoo_website(info.get('website')):
        info['website'] = ''
    if module_name in IAP_SERVICE_MODULES:
        info['auto_install'] = False
    return info


def _update_brand_web_icon_data(env):
    # menus restricted to base.group_no_one are part of the full list
    menus = env['ir.ui.menu'].with_context({'ir.ui.menu.full_list': True}).search([('web_icon', '!=', False)])
    for m in menus:
        web_icon = m.web_icon
        paths = web_icon.split(',')
        if len(paths) == 2:
            module_name = paths[0]
            image_name = paths[1].split('/')[-1][:-4]
            if image_name in ('board', 'modules', 'settings'):
                module_name = image_name
                web_icon = '%s,static/description/icon.png' % module_name

            module_icon = check_viin_brand_module_icon(module_name)
            if module_icon:
                web_icon_data = m._compute_web_icon_data(web_icon)
                web_icon = _build_viin_web_icon_path_from_image(module_icon)
                vals = {}
                if m.web_icon != web_icon:
                    vals['web_icon'] = web_icon
                if web_icon_data != m.web_icon_data:
                    vals['web_icon_data'] = web_icon_data
                if vals:
                    m.write(vals)


def _update_favicon(env):
    company_model = env['res.company']
    companies = company_model.with_context(active_test=False).search([])
    companies.write({'favicon': company_model._get_default_favicon()})


def _build_viin_web_icon_path_from_image(img_path):
    """Turn an image path into a ``web_icon`` value.

    :param img_path: ``/module_name/path/to/image`` or ``module_name/path/to/image``
    :return: the ``module_name,path/to/image`` form of ``web_icon``
    """
    path = []
    while img_path:
        img_path, basename = os.path.split(img_path)
        if img_path == os.path.sep:
            img_path = ''
        if img_path:
            path.insert(0, basename)
    return '%s,%s' % (basename, os.path.join(*path))


def _compute_web_icon_data_plus(self, web_icon):
    """Replace ``ir.ui.menu._compute_web_icon_data`` to take the menu icon from the Viindoo icon set."""
    paths = web_icon.split(',') if web_icon and isinstance(web_icon, str) else []
    if len(paths) == 2:
        if check_viin_brand_module_icon(paths[0]):
            img_path = get_viin_brand_module_icon(paths[0])
            web_icon = _build_viin_web_icon_path_from_image(img_path)
    return _compute_web_icon_data(self, web_icon)


def _disable_core_webmanifest_tests():
    """Neutralise the core web manifest tests whose assertions the Viindoo manifest invalidates.

    ``WebManifestRoutesTest`` asserts the Odoo name, colour and icons; the equivalent Viindoo
    expectations are asserted by ``tests/test_webmanifest.py``. The tests that this module does
    not change keep running.
    """
    from odoo.addons.web.tests.test_webmanifest import WebManifestRoutesTest

    def pass_test(self):
        pass

    WebManifestRoutesTest.test_apple_touch_icon = pass_test
    WebManifestRoutesTest.test_webmanifest_unauthenticated = pass_test
    WebManifestRoutesTest.test_webmanifest = pass_test
    WebManifestRoutesTest.test_webmanifest_scoped = pass_test


def _patch_test_default_manifest_icon_expectation():
    """Realign ``base.tests.test_module.TestModuleManifest`` to the Viindoo icon.

    ``test_default_manifest`` compares the manifest of a temporary module with a literal dict
    carrying the stock base icon, while the module resolves to the Viindoo base icon. The wrapper
    rewrites only an ``icon`` key equal to the stock path, so every other assertion is unchanged.
    """
    from odoo.addons.base.tests.test_module import TestModuleManifest

    assertDictEqual_orig = TestModuleManifest.assertDictEqual

    def _rebrand_icon(mapping):
        if isinstance(mapping, dict) and mapping.get('icon') == STOCK_BASE_ICON:
            mapping = dict(mapping, icon=get_viin_brand_module_icon('base'))
        return mapping

    def assertDictEqual(self, d1, d2, msg=None):
        return assertDictEqual_orig(self, _rebrand_icon(d1), _rebrand_icon(d2), msg)

    TestModuleManifest.assertDictEqual = assertDictEqual


def _realign_core_pdf_metadata_test():
    """Realign ``base.tests.test_pdf.TestPdf.test_branded_file_writer`` to Viindoo.

    The test reads the creator and producer of a document written by ``BrandedFileWriter`` and
    compares them with ``'Odoo'``, while every written document carries Viindoo. The wrapper turns
    only that expected value into Viindoo, so the test still fails when the writer stops setting
    the entries.
    """
    from unittest.mock import patch

    from odoo.addons.base.tests.test_pdf import TestPdf

    from .tools import PRODUCT_NAME

    test_original = TestPdf.test_branded_file_writer

    @functools.wraps(test_original)
    def test_branded_file_writer(self):
        assert_equal = self.assertEqual

        def assertEqual(first, second, msg=None):
            return assert_equal(first, PRODUCT_NAME if second == 'Odoo' else second, msg)

        with patch.object(self, 'assertEqual', assertEqual):
            return test_original(self)

    TestPdf.test_branded_file_writer = test_branded_file_writer


def post_init_hook(env):
    _update_brand_web_icon_data(env)
    _update_favicon(env)


def uninstall_hook(env):
    # The icon and manifest patches belong to the process, not to this database: other databases
    # served by the same process keep the branding.
    env['ir.module.module']._restore_domain_for_action()


def _patch_pdf_branding():
    """Make every PDF Odoo writes carry Viindoo as its creator and producer.

    ``BrandedFileWriter`` sets both entries to Odoo whenever a document is written, so the writer
    is replaced, and the XMP packet of the document, when it has one, is made to agree with them.
    The signature field a signer creates by default is renamed likewise.
    """
    from odoo.tools import pdf
    from odoo.tools.pdf.signature import PdfSigner

    from .tools import PRODUCT_NAME, brand_xmp

    metadata = {'/Creator': PRODUCT_NAME, '/Producer': PRODUCT_NAME}
    writer = pdf.BrandedFileWriter

    def brand_document_xmp(self):
        xmp = self._root_object.get('/Metadata')
        if xmp is None:
            return
        stream = xmp.get_object()
        content = stream.getData()
        branded = brand_xmp(content)
        if branded != content:
            stream.setData(branded)

    if hasattr(pdf.PdfWriter, 'write_stream'):
        def write_stream(self, *args, **kwargs):
            self.add_metadata(metadata)
            brand_document_xmp(self)
            super(writer, self).write_stream(*args, **kwargs)

        writer.write_stream = write_stream
    else:
        def write(self, *args, **kwargs):
            self.addMetadata(metadata)
            brand_document_xmp(self)
            super(writer, self).write(*args, **kwargs)

        writer.write = write

    sign_pdf = PdfSigner.sign_pdf

    def sign_pdf_viindoo(self, visible_signature=False, field_name="Viindoo Signature", signer=None):
        return sign_pdf(self, visible_signature, field_name, signer)

    PdfSigner.sign_pdf = sign_pdf_viindoo


def post_load():
    if config.get('test_enable', False):
        _disable_core_webmanifest_tests()
        _patch_test_default_manifest_icon_expectation()
        _realign_core_pdf_metadata_test()

    module.get_module_icon = get_viin_brand_module_icon
    module._load_manifest = _load_manifest_plus
    IrUiMenu._compute_web_icon_data = _compute_web_icon_data_plus
    _patch_pdf_branding()
