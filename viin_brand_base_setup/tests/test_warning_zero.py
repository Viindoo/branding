# Module-owned QWeb-directive hygiene guard (DESIGN 4c title-xpath row / ODOO-AI-ETHOS #8).
#
# CONTRACT: viin_brand_base_setup must ship NO deprecated QWeb directive (t-esc / t-raw) in its own
# module-owned view data - it uses the modern t-out directive instead. A re-introduced value-bearing
# t-esc/t-raw in this module MUST fail this test.
#
# TITLE DE-BRAND IS NOW VARIABLE-BASED (not a //title xpath rewrite). The tab title is de-branded to
# "Viindoo" by setting the `title` render variable via `<t t-set="title">Viindoo</t>` in the
# web.webclient_bootstrap-inheriting (backend) and web.login_layout-inheriting (login) templates.
# Core web.layout's own node - `<title t-esc="title or 'Odoo'"/>` (web/views/webclient_templates.xml:22)
# - is left UNTOUCHED and still resolves the rendered title to "Viindoo" through that variable.
#
# WHY the earlier t-out-xpath guards were retired (root cause, ODOO-AI-ETHOS #5/#8): the previous
# de-brand rewrote core's `<title t-esc>` into `t-out` via `<xpath expr="//title">`. That xpath
# cannot be located in the STRIPPED web.layout proxy that core web.WebSuite._check_forbidden_statements
# writes (no <title>, bare <link/>), so it raised ValidationError and broke core's own suite - the
# exact item-A bug. The fix DELETES that fragile xpath and re-homes the de-brand onto the `title`
# variable. Two former guards asserted the retired mechanism directly (that our views ship a
# `<xpath expr="//title">` setting t-out, and that web.layout's COMBINED <title> renders via t-out
# and drops t-esc); both are FALSE BY DESIGN after the fix (core's t-esc node remains; the de-brand
# is variable-based), so they were implementation-coupled false alarms on a correct refactor and were
# removed. The RENDERED title-de-brand BEHAVIOUR they nominally protected - backend and login page
# <title> resolving to "Viindoo" - is now guarded observably in tests/test_debrand_layout.py
# (DebrandHeadRenderTest), including the login page that would regress if a fix branded only the
# backend.
#
# SCOPE NOTE: the t-esc deprecation warning fires ONLY under dev_mode (odoo/addons/base/models/
# ir_qweb.py:2488, `if compile_context.get('dev_mode')`), and core itself ships t-esc on the web.layout
# <title> node and elsewhere - so a normal (non-dev) runbot build does not warn on core's node, and
# core's directives are out of this module's scope. This guard therefore polices only THIS module's
# own view source.

import os

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
VIEWS_DIR = os.path.join(MODULE_DIR, "views")

# QWeb directives deprecated in 19.0 in favour of t-out; a live (value-bearing) occurrence in a
# module-owned template is legacy-directive debt this module must not carry.
DEPRECATED_QWEB_DIRECTIVES = ("t-esc", "t-raw")


def _iter_view_files():
    """Yield (filename, absolute-path) for every module-owned data XML under views/."""
    for name in sorted(os.listdir(VIEWS_DIR)):
        if name.endswith(".xml"):
            yield name, os.path.join(VIEWS_DIR, name)


def _iter_elements(path):
    """Parse a view XML file and yield every element in it (root included)."""
    yield from etree.parse(path).getroot().iter()


def _live_deprecated_directive(element):
    """Return the deprecated directive this element LIVE-introduces, or None.

    Two shapes introduce a deprecated directive onto a rendered node:
      1. a real template node carrying the attribute directly: ``<span t-esc="x"/>``;
      2. an inherit that SETS a non-empty value: ``<attribute name="t-esc">x</attribute>``.
    An inherit that REMOVES the inherited directive - the empty ``<attribute name="t-esc"/>`` -
    introduces nothing (template_inheritance.py deletes the attribute when the value is empty, which
    is exactly how a combined arch loses t-esc) and is therefore allowed.
    """
    for directive in DEPRECATED_QWEB_DIRECTIVES:
        # shape 1: the directive is a real attribute on a real template node
        if element.get(directive) is not None:
            return directive
    # shape 2: an <attribute name="t-esc">value</attribute> that SETS a non-empty value
    if element.tag == "attribute" and element.get("name") in DEPRECATED_QWEB_DIRECTIVES:
        if (element.text or "").strip():
            return element.get("name")
    return None


@tagged("post_install", "-at_install")
class TitleDebrandSourceGuardTest(TransactionCase):
    """STATIC source guard - deterministic, needs no live instance (reads views/*.xml from disk)."""

    def test_module_views_ship_no_deprecated_qweb_directive(self):
        """No module-owned view may SET a deprecated t-esc/t-raw directive (use the modern t-out)."""
        offenders = []
        for name, path in _iter_view_files():
            for element in _iter_elements(path):
                directive = _live_deprecated_directive(element)
                if directive:
                    offenders.append(
                        "%s: <%s> introduces deprecated directive %r"
                        % (name, element.tag, directive)
                    )
        self.assertFalse(
            offenders,
            "viin_brand_base_setup ships a deprecated QWeb directive in its own view data; use the "
            "modern t-out directive instead. Offenders:\n%s" % "\n".join(offenders),
        )
