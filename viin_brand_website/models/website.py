import base64
import logging

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)

BRAND_FAVICON_PATH = 'viin_brand/static/img/favicon.ico'


class Website(models.Model):
    _inherit = 'website'

    def _default_brand_favicon(self):
        """Brand the favicon a NEWLY CREATED website starts with.

        Core's website.favicon (website/models/website.py) defaults to Odoo's own
        web/static/img/favicon.ico. A Viindoo deployment should start branded.

        This is deliberately a DATA-level default rather than a QWeb override.
        views/website_templates.xml used to carry an
        `<xpath expr="//t[@t-set='x_icon']" position="replace">` that hardcoded the
        brand path into the rendered layout. That made the field unusable: because
        locate_node resolves an xpath to the first document-order match, the
        replace landed on website's own `t-set x_icon` producer and destroyed it,
        so a customer who configured their own favicon could never serve it. A
        default keeps both properties - branded out of the box, and still the
        customer's own value the moment they set one.

        Read by path rather than through a module dependency: viin_brand is
        auto_install and always present in a branded deployment, but this module
        declares no edge to it, so a missing file degrades to core's default
        rather than breaking website creation.
        """
        try:
            with tools.file_open(BRAND_FAVICON_PATH, 'rb') as f:
                return base64.b64encode(f.read())
        except (FileNotFoundError, OSError):
            _logger.warning(
                "%s not found on the addons path; falling back to core's default favicon",
                BRAND_FAVICON_PATH,
            )
            return super()._default_favicon()

    # Redeclared, not just overridden. Core binds the default to the FUNCTION OBJECT
    # (`default=_default_favicon` at class-definition time), so overriding the method
    # alone would never be picked up. to_base.res_company does the same thing for the
    # company favicon, for the same reason.
    favicon = fields.Binary(default=lambda self: self._default_brand_favicon())
