# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.fields import Domain
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval

from odoo.addons.viin_brand_website import uninstall_hook

THEMES_HIDDEN = "['!', ('name', '=like', 'theme_%')]"


@tagged("post_install", "-at_install")
class TestWebsiteAppsAction(TransactionCase):
    """The Apps list of the website offers nothing that only Enterprise can give."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Module = cls.env["ir.module.module"]
        cls.website_apps = cls.env.ref("website.action_website_add_features")
        cls.base_apps = cls.env.ref("base.open_module_tree")
        cls.stub = cls.Module.create({"name": "enterprise_stub_website_apps", "to_buy": True, "state": "uninstallable"})
        cls.theme = cls.Module.create({"name": "theme_stub_website_apps", "state": "uninstalled"})

    def _listed(self, action):
        domain = Domain(safe_eval(action.domain)) if action.domain else Domain.TRUE
        return self.Module.search(domain & Domain("id", "in", (self.stub | self.theme).ids))

    def test_the_website_list_is_one_of_the_apps_lists_of_the_brand(self):
        self.assertIn(self.website_apps, self.Module._get_apps_actions())
        self.assertIn(self.base_apps, self.Module._get_apps_actions())

    def test_the_website_list_hides_the_enterprise_stubs_and_keeps_its_own_themes_filter(self):
        self.website_apps.domain = THEMES_HIDDEN

        for _updated_twice in range(2):
            self.Module._update_domain_for_action()

        self.assertFalse(self._listed(self.website_apps), "stubs and themes stay out of the website list")
        self.assertEqual(self.website_apps.domain.count("to_buy"), 1, "the condition is added once")
        self.assertIn("theme_", self.website_apps.domain)

    def test_a_missing_website_list_does_not_break_the_update_of_the_lists(self):
        self.env["ir.model.data"].search([
            ("module", "=", "website"), ("name", "=", "action_website_add_features"),
        ]).unlink()

        actions = self.Module._get_apps_actions()
        self.Module._update_domain_for_action()

        self.assertIn(self.base_apps, actions)
        self.assertNotIn(self.website_apps, actions)

    def test_uninstalling_the_module_gives_the_website_list_its_domain_back_and_leaves_the_base_list_alone(self):
        self.website_apps.domain = THEMES_HIDDEN
        self.Module._update_domain_for_action()
        self.assertIn("to_buy", self.base_apps.domain)
        self.assertIn("to_buy", self.website_apps.domain)

        uninstall_hook(self.env)

        self.assertNotIn("to_buy", self.website_apps.domain)
        self.assertIn("theme_", self.website_apps.domain, "the themes filter is the website's own")
        self.assertIn("to_buy", self.base_apps.domain, "the base list still belongs to the brand")
