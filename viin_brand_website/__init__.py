import base64
import logging

from odoo import tools

from . import models

_logger = logging.getLogger(__name__)


def _brand_untouched_favicons(env):
    """Give the Viindoo favicon to the websites that still carry core's stock one.

    A field default applies only when a record is created, so it never reaches
    ``website.default_website`` (created while ``website`` loads) nor a website that
    predates this module. Only a favicon byte-identical to core's default is replaced;
    any other value was chosen by someone and is kept.
    """
    Website = env['website'].sudo()
    websites = Website.search([])
    if not websites:
        return

    try:
        with tools.file_open('web/static/img/favicon.ico', 'rb') as f:
            core_default = base64.b64encode(f.read())
    except (FileNotFoundError, OSError):
        # Without the reference value "untouched" cannot be told from "configured".
        _logger.warning("Core favicon not readable; leaving every website favicon untouched.")
        return

    brand_favicon = Website._default_brand_favicon()
    if brand_favicon == core_default:
        # The brand asset is missing and the default fell back to core's favicon.
        return

    untouched = websites.filtered(lambda w: w.favicon == core_default)
    if not untouched:
        return

    # write() re-encodes the value, so a second run selects nothing.
    untouched.write({'favicon': brand_favicon})
    _logger.info(
        "Branded the favicon of %d website(s) that still carried Odoo's default.",
        len(untouched),
    )


def post_init_hook(env):
    _brand_untouched_favicons(env)
