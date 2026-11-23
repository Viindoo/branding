import functools
import logging
import os
import uuid
from urllib.parse import urlparse

from odoo import addons
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


def _is_in_addons_paths(module_name):
    """Tell whether a directory of that name is in the addons paths.

    Unlike the manifest lookup, it never logs: a wrapper of ``Manifest.for_addon`` that drops the
    ``display_warning`` argument makes the lookup of a module that does not exist log a warning.
    """
    return any(os.path.isdir(os.path.join(path, module_name)) for path in addons.__path__)


def check_viin_brand_module_icon(module_name):
    """Find the Viindoo icon of a module.

    The icon is either ``/viin_brand_<module>/static/description/icon.png`` or
    ``/viin_brand/static/img/apps/<module>.png``.

    :param module_name: technical name of the module whose icon is looked up
    :return: the icon path, or ``False`` when no Viindoo icon exists
    """
    brand_module_name = 'viin_brand_%s' % (
        module_name if module_name not in ('general_settings', 'modules') else 'base')
    brand_module_path = _is_in_addons_paths(brand_module_name) and get_module_path(
        brand_module_name, display_warning=False,
    )
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


def _checksum(binary_value):
    """Return the checksum of a binary value, ``False`` when it is empty."""
    return binary_value and binary_value.checksum


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
                if _checksum(web_icon_data) != _checksum(m.web_icon_data):
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


def _update_document_layout_colours(env):
    """Give the companies that never chose a colour of the document layout the colours of the brand.

    Only a company whose primary and secondary colours are both empty is changed; a colour that a
    company holds, even only one of the two, is its own choice.
    """
    # sudo: the hook runs at install with no user, over every company
    companies = env['res.company'].sudo().search([
        ('primary_color', '=', False),
        ('secondary_color', '=', False),
    ])
    companies.write(env['res.company'].default_get(['primary_color', 'secondary_color']))


def post_init_hook(env):
    _update_brand_web_icon_data(env)
    _update_favicon(env)
    _update_document_layout_colours(env)


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
        content = stream.get_data()
        branded = brand_xmp(content)
        if branded != content:
            stream.set_data(branded)

    def write_stream(self, *args, **kwargs):
        self.add_metadata(metadata)
        brand_document_xmp(self)
        super(writer, self).write_stream(*args, **kwargs)

    writer.write_stream = write_stream

    write_signature_placeholder = PdfSigner.write_signature_placeholder

    @functools.wraps(write_signature_placeholder)
    def write_signature_placeholder_viindoo(self, sig_overlay_pdf=None, field_name=None, appearance_origin=None):
        # a unique name, so that signing a document again never collides with an existing field
        field_name = field_name or f"{PRODUCT_NAME} Signature {uuid.uuid4()}"
        return write_signature_placeholder(self, sig_overlay_pdf, field_name, appearance_origin)

    PdfSigner.write_signature_placeholder = write_signature_placeholder_viindoo


def post_load():
    if config.get('test_enable', False):
        _disable_core_webmanifest_tests()

    controllers.database.patch_database_manager()
    module.get_module_icon = get_viin_brand_module_icon
    module._load_manifest = _load_manifest_plus
    IrUiMenu._compute_web_icon_data = _compute_web_icon_data_plus
    _patch_pdf_branding()
