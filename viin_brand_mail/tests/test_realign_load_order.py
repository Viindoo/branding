from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRealignLoadOrder(TransactionCase):
    """The realignment of the google_calendar sync tests exists only if this module loads first.

    The sync tests of google_calendar run right after google_calendar loads, and modules load by
    graph depth. A dependency that moves viin_brand_mail to the depth of google_calendar or deeper
    leaves those tests unrealigned.
    """

    def _depth(self, module_name, cache=None):
        cache = {} if cache is None else cache
        if module_name not in cache:
            module = self.env["ir.module.module"].search([("name", "=", module_name)])
            cache[module_name] = 1 + max(
                (self._depth(dependency.name, cache) for dependency in module.dependencies_id),
                default=0,
            )
        return cache[module_name]

    def test_viin_brand_mail_loads_before_google_calendar(self):
        if not self.env["ir.module.module"].search_count([("name", "=", "google_calendar")]):
            self.skipTest("google_calendar is not available")
        self.assertLess(self._depth("viin_brand_mail"), self._depth("google_calendar"))
