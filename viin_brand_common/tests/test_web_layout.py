from lxml import etree

from odoo.exceptions import ValidationError
from odoo.tests.common import HttpCase, tagged

# The exact arch core writes onto web.layout in WebSuite._check_only_call
# (web/tests/test_js.py:104) so it can read the QUnit asset bundles outside a
# request context. Pinned as a literal on purpose: if core ever changes this
# stub, the failure must surface loudly here instead of letting the real
# defect resurface unnoticed.
WEB_LAYOUT_QUNIT_STUB = (
    '<t t-name="web.layout">'
    '<head><meta charset="utf-8"/><t t-esc="head"/></head>'
    "</t>"
)

BRAND_TITLE = "Viindoo"
BRAND_FAVICON = "/viin_brand/static/img/favicon.ico"
CORE_FAVICON = "/web/static/img/favicon.ico"
CUSTOM_FAVICON = "/test/custom-favicon.ico"


@tagged("-at_install", "post_install")
class TestWebLayoutBrandDefaults(HttpCase):
    """
    The brand defaults viin_brand_common puts on web.layout - title and
    favicon - are FALLBACKS: they must appear wherever nothing else supplies
    a value, must never pre-empt a value someone else supplied, and must
    survive core rewriting web.layout's arch to a stub.

    Viindoo/branding#654: core's WebSuite.test_check_suite replaces
    web.layout's whole arch_db with a minimal stand-in that has a <head> but
    no <title> and no <link>. That write fires ir.ui.view's
    @api.constrains('arch_db') _check_xml, which recombines every EXTENSION
    of web.layout - viin_brand_common.web_layout included. An xpath anchored
    on a node the stand-in lacks breaks the recombination, and the test that
    then errors is precisely the one keeping a stray QUnit.only() from
    silently disabling the entire JS suite.

    Everything below asserts OBSERVABLE output - rendered HTML, or the
    recombined arch web.layout actually ends up with - never the arch string
    of viin_brand_common's own template. The fix for #654 necessarily MOVES
    the node carrying the defaults, so an assertion on our own arch would
    lock in one implementation and turn the correct fix into a false alarm.
    """

    def _brand_title_default_nodes(self, combined_arch):
        """Return every node in ``combined_arch`` that binds ``title`` to the
        brand default.

        Deliberately shape-tolerant - it looks for the behavior ("something
        still binds title to the brand default"), not for one xpath. Two
        shapes count:

        * a ``t-set`` of ``title`` carrying the brand in its value or text,
          e.g. ``<t t-set="title" t-value="title or 'Viindoo'"/>``
        * a ``<title>`` element carrying the brand in an attribute or its
          text, e.g. ``<title t-esc="title or 'Viindoo'"/>``
        """
        found = []
        for node in combined_arch.iter():
            if not isinstance(node.tag, str):
                continue  # comments and processing instructions
            carries_brand = any(
                BRAND_TITLE in value
                for value in list(node.attrib.values()) + [node.text or ""]
            )
            if not carries_brand:
                continue
            if node.get("t-set") == "title" or etree.QName(node).localname == "title":
                found.append(node)
        return found

    def test_brand_title_default_survives_core_qunit_stub_of_web_layout(self):
        """Core must be able to stub web.layout without the brand being lost.

        Two halves, and both are load-bearing. The write must not raise -
        while it does, /web:WebSuite.test_check_suite errors on every Viindoo
        database and its QUnit.only()/QUnit.debug() leak guard is dead. And
        the brand default must still be there afterwards - otherwise deleting
        viin_brand_common's web.layout extension would "fix" #654 by throwing
        away the branding the module exists to provide.
        """
        layout = self.env.ref("web.layout")
        try:
            layout.write({"arch_db": WEB_LAYOUT_QUNIT_STUB})
        except ValidationError as exc:
            self.fail(
                "web.layout must accept the stub arch core writes in "
                "WebSuite._check_only_call (web/tests/test_js.py:104); while "
                "it does not, core's QUnit leak guard is disabled on every "
                "Viindoo database (Viindoo/branding#654). Raised: %s" % exc
            )

        combined_arch = etree.fromstring(layout.get_combined_arch())
        self.assertTrue(
            self._brand_title_default_nodes(combined_arch),
            "once core has stubbed web.layout, its combined arch must STILL "
            "bind title to the '%s' default - dropping the extension is not a "
            "fix for #654, it is a loss of branding" % BRAND_TITLE,
        )

    def test_backend_page_falls_back_to_brand_title_and_favicon(self):
        """With no title and no x_icon supplied, a backend page shows the
        Viindoo brand, never Odoo's."""
        self.authenticate("admin", "admin")
        response = self.url_open("/web")
        self.assertEqual(response.status_code, 200)
        document = response.text
        self.assertEqual(
            document.count("<title>"),
            1,
            "exactly one <title> must render - a second one would mean the "
            "brand default is emitted alongside another producer instead of "
            "falling back to it",
        )
        self.assertIn(
            "<title>%s</title>" % BRAND_TITLE,
            document,
            "the default backend title must be the brand, not core's 'Odoo'",
        )
        self.assertIn(
            'href="%s"' % BRAND_FAVICON,
            document,
            "the default favicon must be the brand one",
        )
        self.assertNotIn(
            CORE_FAVICON,
            document,
            "core's own favicon must not reach the rendered page",
        )

    def test_explicit_title_wins_over_brand_default(self):
        """A page that supplies its own title keeps it.

        viin_brand_common's own /web/offline page sets <t t-set="title">
        Offline</t> in its t-call="web.layout" body. This is the assertion
        that fails if the brand default is ever expressed as an
        unconditional assignment rather than a fallback.
        """
        response = self.url_open("/web/offline")
        self.assertEqual(response.status_code, 200)
        document = response.text
        self.assertEqual(document.count("<title>"), 1)
        self.assertIn(
            "<title>Offline</title>",
            document,
            "the title the page supplied must survive",
        )
        self.assertNotIn(
            "%s</title>" % BRAND_TITLE,
            document,
            "the brand fallback must not overwrite a supplied title",
        )

    def test_explicit_favicon_wins_over_brand_default(self):
        """A page that supplies its own x_icon keeps it.

        No shipped route sets x_icon explicitly, so one is injected into the
        offline page's own t-call body by editing the PARSED tree and writing
        it back - never a string patch of the arch - and rolled back with the
        test savepoint. The assertion is on the rendered HTML, not on the arch.
        """
        offline_view = self.env.ref("viin_brand_common.webclient_offline")
        arch = etree.fromstring(offline_view.arch_db)
        title_nodes = arch.xpath(".//t[@t-set='title']")
        self.assertTrue(
            title_nodes,
            "fixture setup: no <t t-set=\"title\"> found in "
            "viin_brand_common.webclient_offline - update this fixture if "
            "that template changed",
        )
        x_icon_node = etree.Element("t", {"t-set": "x_icon"})
        x_icon_node.text = CUSTOM_FAVICON
        title_nodes[0].addnext(x_icon_node)
        offline_view.write({"arch_db": etree.tostring(arch, encoding="unicode")})

        response = self.url_open("/web/offline")
        self.assertEqual(response.status_code, 200)
        document = response.text
        self.assertIn(
            'href="%s"' % CUSTOM_FAVICON,
            document,
            "the x_icon the page supplied must survive",
        )
        self.assertNotIn(
            BRAND_FAVICON,
            document,
            "the brand fallback must not overwrite a supplied x_icon",
        )
