# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# RED-carrier for BUG S20-1 (rb633-accept-20260808-k4x9-acceptance-report.md).
#
# The Website "Info" page (/website/info) renders its BODY correctly de-branded already:
# viin_brand_website/views/website_templates.xml inherits `website.show_website_info` (the
# INNER content template) and fixes the h1/paragraph/links. But the browser tab <title> still
# leaks "Odoo Information | <website name>", because core resolves that title from a DIFFERENT
# view record - the OUTER wrapper `website.website_info` - and nothing in this module touches it:
#
#   - core website/controllers/main.py website_info() (~line 344-354) calls
#     request.render('website.website_info', values) without setting values['main_object'].
#   - core website/models/ir_ui_view.py _render_template() (line 454-455): when 'main_object' is
#     absent, it defaults to the resolved ir.ui.view record for the template being rendered - i.e.
#     the `website.website_info` view record itself.
#   - core website/views/website_templates.xml, the website.layout title xpath (~line 106-119):
#     `if not additional_title and main_object and 'name' in main_object: additional_title =
#     main_object.sudo().name`, then `title = (additional_title + ' | ' if additional_title else
#     '') + website.name`.
#   - core website/views/website_templates.xml line 2721:
#     `<template id="website_info" name="Odoo Information">` - that `name=` attribute IS the
#     ir.ui.view.name field for that record, so main_object.name == "Odoo Information", giving
#     title == "Odoo Information | <website.name>".
#
# viin_brand_website currently only inherits `website.show_website_info` (a DIFFERENT view record,
# the inner content) and never updates `website.website_info` (the outer wrapper whose own `name`
# field feeds the title). The fix is a plain field-only record update of website.website_info's
# `name` (no arch/xpath needed - `name` is a top-level ir.ui.view field, not part of arch); this
# test is RED before that fix lands and must go GREEN once it does.
#
# Route is public (auth="public"), so this is driven anonymously - matching the confirmed live
# repro (any role, no login needed).
import re

from odoo.tests.common import HttpCase, tagged

# Regex mirrors viin_brand_common/tests/test_debrand_layout.py's _TITLE_RE convention.
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

VIINDOO_INFO_TITLE_MARKER = "Viindoo Information"
ODOO_BRAND_NAME = "Odoo"


@tagged("post_install", "-at_install")
class WebsiteInfoPageTitleTest(HttpCase):
    """Protect that the Website Info page's browser-tab <title> is de-branded, not just its body."""

    def _html_title(self, html):
        match = _TITLE_RE.search(html)
        return match.group(1).strip() if match else None

    def test_website_info_page_title_is_viindoo_not_odoo(self):
        """GET /website/info: the <title> tag must show Viindoo, never the core 'Odoo Information'.

        Body de-brand (h1/paragraph/links) is already correct via show_website_info and is
        deliberately NOT re-asserted here. This guards the OUTER website.website_info view's
        `name` field, which core's website.layout title xpath falls back to when no explicit
        website_meta_title override applies."""
        response = self.url_open("/website/info")
        self.assertEqual(
            response.status_code, 200,
            "Website Info page must render (no ParseError)",
        )
        title = self._html_title(response.text)
        self.assertIsNotNone(title, "Website Info page must render a <title> element")
        self.assertIn(
            VIINDOO_INFO_TITLE_MARKER, title,
            "Website Info page <title> must be de-branded to '%s' (got %r)"
            % (VIINDOO_INFO_TITLE_MARKER, title),
        )
        self.assertNotIn(
            ODOO_BRAND_NAME, title,
            "Website Info page <title> must not leak the '%s' wordmark (got %r) - core's "
            "website.website_info view record still carries name='Odoo Information', which "
            "website.layout's title xpath falls back to via main_object.name"
            % (ODOO_BRAND_NAME, title),
        )
