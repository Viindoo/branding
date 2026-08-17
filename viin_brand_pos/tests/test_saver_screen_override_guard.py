# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Static guard: this module's OWL-template ``t-inherit`` xpath overrides must
still resolve against the templates core actually ships on this series.

RED today (before the production fix): ``viin_brand_pos/static/src/app/
screens/saver_screen.xml`` anchors ``<xpath expr="//div/img" position=
"attributes">`` against ``point_of_sale.SaverScreen`` (core file
``addons/point_of_sale/static/src/app/screens/saver_screen/saver_screen.xml``)
- whose 19.0 body carries NO ``<img>`` at all, only a
``<div class="pos-logo w-100 h-25"/>``. OWL resolves this xpath LAZILY, at
first render (``web/static/src/core/template_inheritance.js``'s
``applyInheritance``/``getElement``), so this class of defect surfaces as a
runtime ``OwlError`` ("cannot be located in element tree") that destroys the
whole POS app - not as a build-time or module-install failure, and not
something a plain ``-i``/``-u`` catches.

This guard reproduces the SAME xpath-location step OWL performs - an XPath
query against the parsed core template - server-side and instantly, using
Odoo's own ``hasclass()`` XPath extension (registered process-wide by
``odoo.addons.base.models.ir_ui_view`` the moment the ``base`` module's
models are imported, which every live registry guarantees; see that file's
``_hasclass``/``xpath_utils`` and ``template_inheritance.js``'s own comment
"hasclass does not exist in XPath 1.0 but is a custom function defined
server side (see _hasclass) usable in lxml"). It never reimplements xpath
resolution and never hardcodes the expected xpath expression: both the
override's xpath and the core template it targets are read from the actual
files on the addons path, resolved through Odoo's own module-path lookup -
so a future core template refactor that breaks the same contract (in this
override, or in one added later) is caught here, rather than by a live POS
session going blank after 5 idle minutes.
"""
import os

from lxml import etree

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)

# (this module's override file, core module owning the target template,
#  core file defining that template) - extend this table for any future
#  t-inherit override this module adds against a core OWL template. The
#  xpath expression(s) themselves are NOT listed here - they are read live
#  from the override file below, so this guard tracks the real source.
_XPATH_OVERRIDE_TARGETS = [
    (
        "static/src/app/screens/saver_screen.xml",
        "point_of_sale",
        "static/src/app/screens/saver_screen/saver_screen.xml",
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
            "sanity: no xpath-override target declared - this guard would "
            "otherwise vacuously pass.",
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
                    "sanity: %r declares no <xpath expr=...> - this guard "
                    "would otherwise vacuously pass for this override."
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
                    "core template %r (module %r) does not resolve to an "
                    "existing file at %r via Odoo's own module-path lookup"
                    % (core_template_rel, core_module, core_template_path),
                )
                core_tree = etree.parse(core_template_path)

                for expr in exprs:
                    with self.subTest(xpath=expr):
                        matches = core_tree.getroot().xpath(expr)
                        self.assertTrue(
                            matches,
                            "%s declares xpath %r against %s (%s), but it "
                            "matches NO element in the core template actually "
                            "shipped on this series. OWL resolves this "
                            "LAZILY at first render "
                            "(template_inheritance.js's applyInheritance/"
                            "getElement), so a broken xpath here surfaces as "
                            "a runtime OwlError ('cannot be located in "
                            "element tree') that destroys the whole POS app "
                            "- not as an install-time failure."
                            % (override_rel, expr, core_module, core_template_rel),
                        )
