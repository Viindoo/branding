# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# A dark-preference user's very first page load of a brand-new browser session must already be dark
# end-to-end with this module installed. The module boots a plugin that reconciles the scheme with the
# stored preference and writes the `color_scheme` cookie after its own read resolves; that write must
# agree with the server's response cookie, never undo it. The viin_brand suite of the same behaviour
# runs without this module, so the race between the plugin and the response cookie is proven here.
import json

from odoo.tests import HttpCase, new_test_user, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _normalize_colour,
)
from odoo.addons.viin_brand.tests.test_scheme_cookie_first_load import (
    _MEASURE_PIVOT_JS,
    _wrap,
)

_SCHEME_STATE_JS = """
await __waitFor(() => document.cookie.includes('color_scheme='), 15000);
await __setParam(%(scheme_key)r, JSON.stringify({
    paint: document.documentElement.dataset.bsTheme,
    cookie: document.cookie,
}));
"""


@tagged('post_install', '-at_install')
class TestSchemeFirstLoadWithTheme(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env['res.partner'].create([
            {'name': 'Dark First Load Fixture Partner %d' % index} for index in range(3)
        ])
        view = cls.env['ir.ui.view'].create({
            'name': 'Dark First Load With Theme Pivot (test)',
            'model': 'res.partner',
            'type': 'pivot',
            'arch': '<pivot/>',
        })
        cls.action = cls.env['ir.actions.act_window'].create({
            'name': 'Dark First Load With Theme Pivot (test)',
            'res_model': 'res.partner',
            'view_mode': 'pivot',
            'view_id': view.id,
        })
        # base.group_system is needed only because the measurement round-trips a value through
        # ir.config_parameter.set_str, which base restricts to that group.
        cls.dark_user = new_test_user(
            cls.env, login='viin_theme_dark_first_load',
            groups='base.group_user,base.group_system',
            viin_color_scheme='dark',
        )

    def _read_json_param(self, key):
        # The browser's requests run on a different test cursor than self.env's (same transaction,
        # separate cache): invalidate before reading back what it wrote.
        self.env.invalidate_all()
        # sudo: reads back a parameter the browser wrote as a system user; the test user may not
        raw = self.env['ir.config_parameter'].sudo().get_str(key)
        self.assertTrue(raw, "the browser-side measurement never reported a value under %r" % key)
        return json.loads(raw)

    def test_a_dark_preference_user_stays_dark_when_the_theme_reconciles_the_scheme(self):
        pivot_key = 'viin_backend_theme.scheme_first_load_test.pivot_surfaces'
        scheme_key = 'viin_backend_theme.scheme_first_load_test.scheme_state'
        code = _wrap(
            (_MEASURE_PIVOT_JS % {'pivot_key': pivot_key})
            + (_SCHEME_STATE_JS % {'scheme_key': scheme_key})
        )
        self.browser_js(
            '/odoo/action-%d' % self.action.id, code, login=self.dark_user.login, timeout=90,
        )

        pivot = self._read_json_param(pivot_key)
        text = _normalize_colour(pivot['textColor'])
        background = _normalize_colour(pivot['bg'])
        ratio = _contrast_ratio(text, background)
        self.assertGreaterEqual(
            round(ratio, 2), WCAG_AA_NORMAL_TEXT,
            "the pivot of a dark-preference user's first load measures only %.2f:1 (%s on %s)"
            % (ratio, text, background),
        )

        state = self._read_json_param(scheme_key)
        self.assertEqual(state['paint'], 'dark')
        self.assertIn('color_scheme=dark', state['cookie'])
