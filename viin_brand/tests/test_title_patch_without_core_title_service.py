import re

from odoo.modules import Manifest
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.js_transpiler import transpile_javascript, url_to_module_path

PATCH = "viin_brand/static/src/core/browser/title_service.js"
CORE_TITLE_SERVICE = "web/static/src/core/browser/title_service.js"
DEFINE_RE = re.compile(r'odoo\.define\(\s*["\']([^"\']+)["\']\s*,\s*\[([^\]]*)\]')


@tagged("post_install", "-at_install")
class TestTitlePatchWithoutCoreTitleService(TransactionCase):
    """A bundle may drop core's title service (the livechat embed does in web.assets_frontend).

    viin_brand lists its title patch in the bundles that keep the service and, being server-wide,
    in the ones of modules that are not installed; the patch must load wherever core's service is
    absent, as the module loader refuses a module whose dependency is not defined.
    """

    def _patch_dependencies(self):
        path = Manifest.for_addon("viin_brand").path + "/static/src/core/browser/title_service.js"
        with open(path, encoding="utf-8") as source:
            transpiled = transpile_javascript("/" + PATCH, source.read())
        match = DEFINE_RE.search(transpiled)
        self.assertTrue(match, "the title patch is not a transpiled module")
        return set(re.findall(r'["\']([^"\']+)["\']', match.group(2)))

    def test_title_patch_loads_in_a_bundle_without_the_core_title_service(self):
        paths = [
            path.lstrip("/")
            for path, _full, _bundle, _mtime in self.env["ir.asset"]._get_asset_paths(
                bundle="web.assets_frontend", assets_params={}
            )
        ]
        defined = {
            url_to_module_path("/" + path)
            for path in paths
            if path.endswith(".js") and path != CORE_TITLE_SERVICE
        }
        missing = self._patch_dependencies() - defined
        self.assertFalse(
            missing,
            "the title patch needs modules a bundle without core's title service does not define",
        )
