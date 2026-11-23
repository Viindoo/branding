# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Every OWL-template ``t-inherit`` xpath override of this module resolves against the core template.

OWL applies the xpath lazily, at the first render, so an xpath that matches nothing surfaces as a
runtime ``OwlError`` ("cannot be located in element tree") that destroys the whole POS app, not as
an install-time failure. The guard runs the same XPath query server-side against the parsed core
template, with the ``hasclass()`` extension Odoo registers for its views. Both the override's xpath
and the core template are read from the files on the addons path.
"""
import os

from lxml import etree

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (this module's override file, core module owning the target template, core file defining it);
# the xpath expressions are read from the override file.
_XPATH_OVERRIDE_TARGETS = [
    (
        "static/src/app/screens/saver_screen.xml",
        "point_of_sale",
        "static/src/app/screens/saver_screen/saver_screen.xml",
    ),
    (
        "static/src/app/navbar/navbar.xml",
        "point_of_sale",
        "static/src/app/components/navbar/navbar.xml",
    ),
    (
        "static/src/customer_display/customer_display.xml",
        "point_of_sale",
        "static/src/customer_display/customer_display.xml",
    ),
    (
        "static/src/backend/lna_checklist/lna_checklist.xml",
        "point_of_sale",
        "static/src/backend/lna_checklist/lna_checklist.xml",
    ),
]


def _iter_xpath_exprs(xml_path):
    tree = etree.parse(xml_path)
    for xpath_el in tree.getroot().iter("xpath"):
        expr = xpath_el.get("expr")
        if expr:
            yield expr


@tagged("post_install", "-at_install")
class TestViinBrandPosSaverScreenXpathResolvesAgainstCore(TransactionCase):
    def test_every_xpath_override_resolves_against_the_shipped_core_template(self):
        self.assertGreater(
            len(_XPATH_OVERRIDE_TARGETS), 0,
            "no xpath-override target declared: this guard would vacuously pass",
        )
        for override_rel, core_module, core_template_rel in _XPATH_OVERRIDE_TARGETS:
            with self.subTest(override=override_rel, core_module=core_module):
                override_path = os.path.join(MODULE_DIR, override_rel)
                self.assertTrue(
                    os.path.isfile(override_path),
                    "declared override file %r does not exist under %r"
                    % (override_rel, MODULE_DIR),
                )
                exprs = list(_iter_xpath_exprs(override_path))
                self.assertGreater(
                    len(exprs), 0,
                    "%r declares no <xpath expr=...>: this guard would vacuously pass for it"
                    % override_rel,
                )

                core_module_path = get_module_path(core_module, display_warning=False)
                self.assertTrue(
                    core_module_path,
                    "core module %r cannot be found on the addons path"
                    % core_module,
                )
                core_template_path = os.path.join(core_module_path, core_template_rel)
                self.assertTrue(
                    os.path.isfile(core_template_path),
                    "core template %r (module %r) does not exist at %r"
                    % (core_template_rel, core_module, core_template_path),
                )
                core_tree = etree.parse(core_template_path)

                for expr in exprs:
                    with self.subTest(xpath=expr):
                        matches = core_tree.getroot().xpath(expr)
                        self.assertTrue(
                            matches,
                            "%s declares xpath %r against %s (%s), but it matches no element "
                            "of the core template"
                            % (override_rel, expr, core_module, core_template_rel),
                        )
