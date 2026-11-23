# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The website builder tests of core compare the computed colour of the builder with core's own
# palette, through the production frontend bundle that the builder iframe loads. That bundle is the
# one users get, so it stays branded; the two core test files that read it are carried here with the
# literals the brand changes realigned (viin_brand_website/__manifest__.py replaces the core files
# in web.assets_unit_tests). A copy is the core file plus exactly the realignments below, under a
# comment header that names the original and its licence (the header is the one part not compared):
# when core changes the file, or a brand colour changes, the copy no longer matches and this test
# names the line to bring up to date.
import difflib
import re

from odoo.modules.module import get_manifest
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_path

from odoo.addons.viin_brand.tests.test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

UNIT_BUNDLE = "web.assets_unit_tests"
CORE_DIR = "website/static/tests/builder"
COPY_DIR = "viin_brand_website/static/tests/builder/core_copies"
CORE_PRIMARY = "rgb(113, 75, 103)"
CORE_CONTRAST_DARK = "rgb(33, 37, 41)"
HELPERS = "@website/../tests/builder/"
S_TABS_IMPORT = 'import { defineWebsiteModels, setupWebsiteBuilderWithSnippet } from "./website_helpers";'
IMAGE_SHAPE_HELPERS_IMPORT = 'import { onRpcImg, testImg, testSvgImg, testSvgImgSrc } from "./image_test_helpers";'
WEBSITE_HELPERS_IMPORT = '} from "./website_helpers";'

# file -> {core text: number of occurrences the realignment covers}
COPIED_TESTS = {
    "s_tabs.test.js": {
        S_TABS_IMPORT: 1,
        CORE_PRIMARY: 1,
        CORE_CONTRAST_DARK: 1,
    },
    "image_shape.test.js": {
        WEBSITE_HELPERS_IMPORT: 1,
        IMAGE_SHAPE_HELPERS_IMPORT: 1,
        CORE_PRIMARY: 2,
    },
}


def _rgb(hex_colour):
    digits = hex_colour.lstrip("#")
    return "rgb(%d, %d, %d)" % tuple(int(digits[i:i + 2], 16) for i in (0, 2, 4))


@tagged("post_install", "-at_install")
class TestCoreTestCopies(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            scss = scss_file.read()
        cls.realigned = {
            CORE_PRIMARY: _rgb(_resolve_scss_hex(scss, "$o-enterprise-color")),
            CORE_CONTRAST_DARK: _rgb(_resolve_scss_hex(scss, "$color-contrast-dark")),
            # The copy lives in another module, so the helpers are named by module; a longer line is
            # wrapped as the repository's formatter wants it.
            S_TABS_IMPORT: (
                "import {\n    defineWebsiteModels,\n    setupWebsiteBuilderWithSnippet,\n}"
                ' from "%swebsite_helpers";' % HELPERS
            ),
            IMAGE_SHAPE_HELPERS_IMPORT: (
                "import {\n    onRpcImg,\n    testImg,\n    testSvgImg,\n    testSvgImgSrc,\n}"
                ' from "%simage_test_helpers";' % HELPERS
            ),
            WEBSITE_HELPERS_IMPORT: '} from "%swebsite_helpers";' % HELPERS,
        }

    def _read(self, path):
        with open(file_path(path), encoding="utf-8") as source:
            return source.read()

    def _split_header(self, text):
        """The comment lines the copy carries on top, and the rest of the file."""
        lines = text.splitlines(keepends=True)
        header_size = 0
        while header_size < len(lines) and lines[header_size].startswith("//"):
            header_size += 1
        return "".join(lines[:header_size]), "".join(lines[header_size:])

    def _realigned_core(self, name):
        text = self._read("%s/%s" % (CORE_DIR, name))
        for core_text, count in COPIED_TESTS[name].items():
            self.assertEqual(
                text.count(core_text), count,
                "core's %s now holds %s x %s: review the copy and its realignments"
                % (name, text.count(core_text), core_text),
            )
            text = text.replace(core_text, self.realigned[core_text])
        return text

    def test_a_copy_is_the_core_test_with_only_the_realigned_literals_changed(self):
        for name in COPIED_TESTS:
            with self.subTest(name):
                expected = self._realigned_core(name)
                _header, copy = self._split_header(self._read("%s/%s" % (COPY_DIR, name)))
                diff = [
                    line for line in difflib.unified_diff(
                        expected.splitlines(), copy.splitlines(), "core", "copy", n=0, lineterm=""
                    )
                ][:12]
                self.assertEqual(copy, expected, "%s drifted from core:\n%s" % (name, "\n".join(diff)))

    def test_a_copy_names_its_original_and_keeps_its_licence(self):
        for name in COPIED_TESTS:
            with self.subTest(name):
                header, _copy = self._split_header(self._read("%s/%s" % (COPY_DIR, name)))

                self.assertIn("%s/%s" % (CORE_DIR, name), header)
                self.assertIn("Modified copy", header)
                self.assertIn("LGPL-3", header)

    def test_the_manifest_replaces_each_core_test_with_its_copy(self):
        replaced = {
            directive[1]: directive[2]
            for directive in get_manifest("viin_brand_website")["assets"][UNIT_BUNDLE]
            if isinstance(directive, tuple) and directive[0] == "replace"
        }
        self.assertEqual(
            replaced,
            {"%s/%s" % (CORE_DIR, name): "%s/%s" % (COPY_DIR, name) for name in COPIED_TESTS},
        )

    def test_the_unit_test_bundle_carries_the_copies_in_place_of_the_core_files(self):
        bundle = self.env["ir.qweb"]._get_asset_bundle(UNIT_BUNDLE, css=False, js=True)
        content = (bundle.js().raw or b"").decode("utf-8", "replace")
        modules = set(re.findall(r'''odoo\.define\(\s*["'](@[^"']+)["']''', content))

        for name in COPIED_TESTS:
            stem = name[:-len(".js")]
            with self.subTest(name):
                self.assertIn("@viin_brand_website/../tests/builder/core_copies/%s" % stem, modules)
                self.assertNotIn("@website/../tests/builder/%s" % stem, modules)
