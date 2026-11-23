# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    _COMMENT_RE,
    _iter_rules,
)

KPI_WRAPPER = ".o_account_dashboard_kpis_wrapper"


@tagged("post_install", "-at_install")
class TestDashboardKpisGap(TransactionCase):

    def _wrapper_margins(self, bundle_name):
        """Return the ``(top, bottom)`` margins after each declaration of the KPI wrapper, in source order.

        The rules of every width are read in order, the media rule of core included: a rule of this
        module placed after them is the one that decides the top margin at each width.
        """
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = _COMMENT_RE.sub("", "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        ))
        states = []
        top = bottom = None
        for _order, selector, body in _iter_rules(css):
            if selector != KPI_WRAPPER:
                continue
            for declaration in body.split(";"):
                name, separator, value = declaration.partition(":")
                name, value = name.strip(), value.strip()
                if not separator:
                    continue
                tokens = value.split()
                if name == "margin" and len(tokens) in (3, 4):
                    top, bottom = tokens[0], tokens[2]
                elif name == "margin" and len(tokens) == 1:
                    top = bottom = tokens[0]
                elif name == "margin-top":
                    top = value
                elif name == "margin-bottom":
                    bottom = value
                else:
                    continue
                states.append((top, bottom))
        self.assertTrue(states, "No compiled rule gives a margin to %s." % KPI_WRAPPER)
        return states

    def test_the_kpi_row_has_the_gap_below_the_control_panel_that_core_gives_below_the_row(self):
        """The top margin of the KPI row is the margin core gives it at the bottom on a desktop, from
        the same token, in the light and in the dark bundle, after the rule of every width of core.

        WOULD FAIL IF REVERTED: without the stylesheet of this module the last rule of the wrapper
        leaves 0 on top; a stylesheet placed before the rules of core is overridden by them."""
        for scheme, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            with self.subTest(scheme=scheme):
                states = self._wrapper_margins(bundle_name)
                top = states[-1][0]
                core_bottom = states[0][1]
                self.assertNotIn(top, ("0", "0px"), "the KPI row has no top margin in the %s bundle" % scheme)
                self.assertEqual(top, core_bottom)
