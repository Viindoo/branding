# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# A dark-preference user's very first page load of a brand-new browser session must already be dark
# end-to-end - the webclient response itself and every lazy-loaded view bundle it triggers.
#
# `ir.http`'s webclient-rendering hook must write the resolved `color_scheme` onto the response
# (`request.future_response.set_cookie('color_scheme', <scheme>)`) whenever it differs from the
# request's own incoming cookie value, and must not re-emit it once the two match. `color_scheme()`
# resolves stored preference > cookie > super(); that precedence is guarded by
# tests/test_color_scheme_pref.py.
#
# Why the response must carry the cookie: `web/static/src/views/view.js` decides whether to
# `loadBundle("web.assets_backend_lazy_dark")` or the light sibling by reading
# `cookie.get("color_scheme")`, a synchronous browser-cookie read. On a session that has never
# received a `color_scheme` cookie that read is empty even for a user whose stored preference is
# dark, so the first pivot/graph opened can load the light lazy bundle. `graph_renderer.js` also
# reads the cookie into a module-level constant, evaluated once per session, so whichever scheme is
# in the cookie when that module first loads freezes the chart's legend/axis colours for the
# session. Core's `ir.http.webclient_rendering_context()` already calls `self.color_scheme()`
# before rendering `web.webclient_bootstrap` for every `/odoo` request; the hook rides that call
# so the cookie arrives with the first HTML response.
#
# The readability tests are an HttpCase rather than a compiled-CSS check because the defect is
# about when a cookie exists relative to when a browser evaluates JS that reads it once. Every
# colour is read from the live browser: `getComputedStyle` for the pivot's text and effective
# background, and the graph's own Chart.js instance (`window.Chart.getChart`) for the legend/axis
# colours.
#
# Each `browser_js` / `start_tour` call is already a fresh context: `HttpCase.browser_js` creates a
# new `ChromeBrowser` per call with its own throwaway `--user-data-dir`, so two calls never share a
# cookie jar, and `HttpCase.authenticate` seeds only the `session_id` cookie, never `color_scheme`.
import json

from odoo.tests import HttpCase, new_test_user, tagged

# `_normalize_colour` accepts both `#rrggbb` and the `rgb()`/`rgba()` strings `getComputedStyle`
# returns.
from .test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _normalize_colour,
)

# JS helpers shared by every browser_js call: a JSON-RPC `ir.config_parameter.set_str` (the
# channel that round-trips a measured value back to this test's transaction, see
# `_read_json_param`), a poll-until-truthy waiter (the webclient mounts views asynchronously), and
# an "effective background" walk (a transparent ancestor must be skipped to find the surface
# behind the text).
_JS_HELPERS = """
async function __setParam(key, value) {
    const resp = await fetch('/web/dataset/call_kw/ir.config_parameter/set_str', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {model: 'ir.config_parameter', method: 'set_str', args: [key, value], kwargs: {}},
        }),
    });
    const data = await resp.json();
    if (data.error) { throw new Error(JSON.stringify(data.error)); }
}
async function __waitFor(predicate, timeoutMs) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
        const result = predicate();
        if (result) { return result; }
        await new Promise((resolve) => setTimeout(resolve, 100));
    }
    throw new Error(
        '__waitFor: timed out waiting for a condition; the page shows: '
        + document.body.innerText.slice(0, 300).replace(/\\s+/g, ' ')
        + ' | has window.Chart: ' + Boolean(window.Chart)
        + ' | canvas: ' + document.querySelectorAll('canvas').length
        + ' | pivot cells: ' + document.querySelectorAll('.o_pivot_cell_value').length
    );
}
function __effectiveBackground(el) {
    let node = el;
    while (node) {
        const bg = getComputedStyle(node).backgroundColor;
        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
            return bg;
        }
        node = node.parentElement;
    }
    return getComputedStyle(document.body).backgroundColor;
}
"""

# Measures a pivot value cell's text colour and its effective background. `.o_pivot_cell_value
# .o_value` is the text-carrying node core renders for any non-boolean measure; the `<td>` ancestor
# carries the `bg-100` surface class, so the background is read from that element.
_MEASURE_PIVOT_JS = """
const __pivotValue = await __waitFor(
    () => document.querySelector('.o_pivot_cell_value .o_value'), 15000
);
const __pivotCell = __pivotValue.closest('.o_pivot_cell_value');
await __setParam(%(pivot_key)r, JSON.stringify({
    textColor: getComputedStyle(__pivotValue).color,
    bg: __effectiveBackground(__pivotCell),
}));
"""

# Measures the graph's live Chart.js instance for the legend colour
# (`chart.legend.legendItems[i].fontColor`, the field Chart.js paints the legend text with) and the
# x/y axis tick colour (`chart.options.scales.<axis>.ticks.color`, the option `graph_renderer.js`
# sets directly). `window.Chart` is the vendored UMD global and `Chart.getChart(canvas)` recovers
# the instance mounted on a `<canvas>`.
_MEASURE_GRAPH_JS = """
const __canvas = await __waitFor(
    () => document.querySelector('.o_graph_renderer canvas'), 15000
);
const __chart = await __waitFor(() => window.Chart && window.Chart.getChart(__canvas), 15000);
await __waitFor(
    () => __chart.legend && __chart.legend.legendItems && __chart.legend.legendItems.length,
    15000
);
const __scales = __chart.options.scales || {};
await __setParam(%(graph_key)r, JSON.stringify({
    legendColor: __chart.legend.legendItems[0].fontColor,
    xTickColor: __scales.x && __scales.x.ticks ? __scales.x.ticks.color : null,
    yTickColor: __scales.y && __scales.y.ticks ? __scales.y.ticks.color : null,
    bg: __effectiveBackground(__canvas),
}));
"""


def _wrap(js_body):
    """Wrap a measurement snippet in the contract `HttpCase.browser_js` polls for:
    `console.log('test successful')` on success, `console.error` on any thrown failure."""
    return _JS_HELPERS + (
        "(async () => {\n"
        "    try {\n"
        "        %s\n"
        "        console.log('test successful');\n"
        "    } catch (e) {\n"
        "        console.error(e && e.message || String(e));\n"
        "    }\n"
        "})();\n"
    ) % js_body.replace("\n", "\n        ")


@tagged('post_install', '-at_install')
class TestSchemeCookieResponseWrite(HttpCase):
    """`ir.http`'s webclient-rendering hook writes the resolved colour scheme onto the response
    cookie exactly when it disagrees with the request's own cookie, and never rewrites it once the
    two agree."""

    def test_response_cookie_converges_to_the_resolved_scheme_and_then_stays_stable(self):
        """A dark-preference user with no `color_scheme` cookie yet gets one written on their very
        first response; a second request, now carrying that cookie, gets no further Set-Cookie for
        it.

        Both halves are one test because "no rewrite once it matches" is only meaningful once the
        cookie has converged through the mechanism's own first response. Both requests go through
        the same `requests.Session`-backed opener, so the second picks up the first response's
        Set-Cookie the way a real browser would.
        """
        user = new_test_user(
            self.env, login='viin_scheme_cookie_write', groups='base.group_user',
            viin_color_scheme='dark',
        )
        self.authenticate(user.login, user.login)

        first = self.url_open('/odoo')
        self.assertEqual(
            first.cookies.get('color_scheme'), 'dark',
            "the first response for a dark-preference user with no incoming color_scheme cookie "
            "must set-cookie color_scheme=dark - webclient_rendering_context() calls "
            "self.color_scheme(), which resolves 'dark' from the stored preference; the response "
            "must carry it so the first lazy pivot/graph bundle sees it without racing an RPC.",
        )

        second = self.url_open('/odoo')
        self.assertNotIn(
            'color_scheme', second.cookies,
            "a second request whose incoming color_scheme cookie already equals the resolved "
            "scheme must not receive another Set-Cookie for it - the write is a convergence, not "
            "an every-request re-assertion.",
        )

    def _rpc_write(self, model, res_id, vals):
        # The RPC channel a real Preferences-form save goes through: res.users.write() must run
        # inside the request's dispatch for request.future_response to exist, and
        # Dispatcher.post_dispatch injects its cookies into the final HTTP response, JSON-RPC
        # included.
        response = self.url_open('/web/dataset/call_kw/%s/write' % model, json={
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'model': model, 'method': 'write', 'args': [[res_id], vals], 'kwargs': {}},
        })
        result = response.json()
        self.assertNotIn('error', result, result.get('error'))
        return response

    def test_response_cookie_syncs_when_a_user_writes_their_own_color_scheme_to_light_or_dark(self):
        """Writing one's own `viin_color_scheme` to `light` or `dark` must sync the `color_scheme`
        response cookie in that same response; otherwise a user who carries the opposite value
        sees no effect until the cookie's year-long expiry."""
        user = new_test_user(
            self.env, login='viin_scheme_cookie_self_write', groups='base.group_user',
            viin_color_scheme='light',
        )
        self.authenticate(user.login, user.login)

        for scheme in ('dark', 'light'):
            with self.subTest(scheme=scheme):
                response = self._rpc_write('res.users', user.id, {'viin_color_scheme': scheme})
                self.assertEqual(
                    response.cookies.get('color_scheme'), scheme,
                    "writing viin_color_scheme=%r on the CURRENTLY LOGGED-IN user's own record "
                    "must set-cookie color_scheme=%r in the same response." % (scheme, scheme),
                )

    def test_response_cookie_is_not_set_when_writing_a_different_users_own_preference(self):
        """The sync is scoped to the acting user's own preference change, like the model's
        user_writeable boundary: an admin changing a different user's preference must not
        change the admin's own response cookie."""
        admin = new_test_user(
            self.env, login='viin_scheme_cookie_admin', groups='base.group_user,base.group_system',
            viin_color_scheme='light',
        )
        target = new_test_user(
            self.env, login='viin_scheme_cookie_target', groups='base.group_user',
            viin_color_scheme='light',
        )
        self.authenticate(admin.login, admin.login)

        response = self._rpc_write('res.users', target.id, {'viin_color_scheme': 'dark'})
        self.assertNotIn(
            'color_scheme', response.cookies,
            "writing a DIFFERENT user's viin_color_scheme must not set a color_scheme cookie on "
            "the ACTING user's own response.",
        )

    def test_switching_to_auto_leaves_the_client_cached_resolution_alone(self):
        """Switching one's own `viin_color_scheme` to `auto` ("System") must not touch the
        `color_scheme` cookie.

        Under 'auto' that cookie is the only place the resolved scheme exists: the client resolves
        the device preference, writes the effective light|dark there, and only then issues this
        write. Expiring it would discard the answer for the reload that follows, and would blank
        the value core's dark-mode clients read (graph colours, the colour picker, the ace editor,
        the pdf.js viewer)."""
        user = new_test_user(
            self.env, login='viin_scheme_cookie_auto_keep', groups='base.group_user',
            viin_color_scheme='dark',
        )
        self.authenticate(user.login, user.login)

        # The browser already carries a resolved scheme, as a real setScheme('auto') leaves it.
        pinned = self._rpc_write('res.users', user.id, {'viin_color_scheme': 'dark'})
        self.assertEqual(
            pinned.cookies.get('color_scheme'), 'dark',
            "the browser was never carrying a resolved scheme, so this test could not observe "
            "whether switching to auto preserves one.",
        )

        response = self._rpc_write('res.users', user.id, {'viin_color_scheme': 'auto'})
        # `response.cookies` drops an expired cookie and `response.headers` collapses repeated
        # headers, so neither would reveal an expiring Set-Cookie; read the raw header list.
        scheme_headers = [
            header for header in response.raw.headers.getlist('Set-Cookie')
            if header.lower().startswith('color_scheme=')
        ]
        self.assertFalse(
            scheme_headers,
            "switching viin_color_scheme to auto must emit no color_scheme Set-Cookie at all - "
            "the imminent reload depends on the resolution already cached there: got %r"
            % scheme_headers,
        )


@tagged('post_install', '-at_install')
class TestPivotGraphFreshContextReadability(HttpCase):
    """A dark-preference user's very first pivot/graph view, in a session that has never received
    a `color_scheme` cookie, must already render with readable (WCAG AA, >= 4.5:1) text, not the
    light lazy bundle a cookie-less first load can otherwise ship.

    The pivot and graph views are throwaway views on `res.partner` created in the test's
    transaction, so they stay inside viin_brand's dependency closure.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Enough records for the pivot/graph aggregation to have data (model.hasData()).
        cls.env['res.partner'].create([
            {'name': 'Dark First Load Fixture Partner %d' % index} for index in range(3)
        ])
        cls.pivot_view = cls.env['ir.ui.view'].create({
            'name': 'Dark Mode First Load Pivot (test)',
            'model': 'res.partner',
            'type': 'pivot',
            'arch': '<pivot/>',
        })
        cls.pivot_action = cls.env['ir.actions.act_window'].create({
            'name': 'Dark Mode First Load Pivot (test)',
            'res_model': 'res.partner',
            'view_mode': 'pivot',
            'view_id': cls.pivot_view.id,
        })
        cls.graph_view = cls.env['ir.ui.view'].create({
            'name': 'Dark Mode First Load Graph (test)',
            'model': 'res.partner',
            'type': 'graph',
            # two groupings: with one, the graph shows no legend of its own
            'arch': '<graph><field name="create_uid"/><field name="lang"/></graph>',
        })
        cls.graph_action = cls.env['ir.actions.act_window'].create({
            'name': 'Dark Mode First Load Graph (test)',
            'res_model': 'res.partner',
            'view_mode': 'graph',
            'view_id': cls.graph_view.id,
        })
        # base.group_system is needed only because the measurement round-trips a value through
        # ir.config_parameter.set_str, which base restricts to that group.
        cls.dark_user = new_test_user(
            cls.env, login='viin_fresh_dark_first_load',
            groups='base.group_user,base.group_system',
            viin_color_scheme='dark',
        )

    def setUp(self):
        super().setUp()
        if "tour_enabled" not in self.env["res.users"]._fields:
            self.skipTest("web_tour is not installed")

    def _read_json_param(self, key):
        # The browser's requests run on a different test cursor than self.env's (same transaction,
        # separate cache): invalidate before reading back what it wrote.
        self.env.invalidate_all()
        # sudo: reads back the parameter the page wrote, whatever the test user can.
        raw = self.env['ir.config_parameter'].sudo().get_str(key)
        self.assertTrue(
            raw,
            "the browser-side measurement never reported a value under %r - the page did not "
            "reach the surface under test" % key,
        )
        return json.loads(raw)

    def _assert_readable(self, label, colour_value, background_value):
        colour = _normalize_colour(colour_value)
        background = _normalize_colour(background_value)
        self.assertIsNotNone(colour, "%s: %r carries no readable colour" % (label, colour_value))
        self.assertIsNotNone(
            background, "%s: effective background %r carries no readable colour" % (label, background_value),
        )
        ratio = _contrast_ratio(colour, background)
        self.assertGreaterEqual(
            round(ratio, 2), WCAG_AA_NORMAL_TEXT,
            "%s: %s on its own effective background %s measures only %.2f:1, below the WCAG AA "
            "normal-text threshold %.1f:1." % (label, colour, background, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_pivot_first_load_then_graph_in_the_same_session_are_both_readable(self):
        """The pivot opened as the very first view in a fresh context is readable; the graph
        opened afterwards, in that same now-dark session, is readable too."""
        pivot_key = 'viin_brand.scheme_first_load_test.pivot_surfaces'
        graph_key = 'viin_brand.scheme_first_load_test.graph_surfaces'
        code = _wrap(
            (_MEASURE_PIVOT_JS % {'pivot_key': pivot_key})
            + (
                "\nconst __env = window.odoo.__WOWL_DEBUG__.root.env;"
                "\nawait __env.services.action.doAction(%d);\n" % self.graph_action.id
            )
            + (_MEASURE_GRAPH_JS % {'graph_key': graph_key})
        )
        self.browser_js(
            '/odoo/action-%d' % self.pivot_action.id, code,
            login=self.dark_user.login, timeout=90,
        )

        pivot = self._read_json_param(pivot_key)
        self._assert_readable('pivot cell text (first view of a fresh context)', pivot['textColor'], pivot['bg'])

        graph = self._read_json_param(graph_key)
        self.assertIsNotNone(
            graph['legendColor'],
            "the graph's Chart.js legend produced no items to read a colour from - "
            "model.hasData() must be true for the fixture partners created in setUpClass.",
        )
        self._assert_readable('graph legend', graph['legendColor'], graph['bg'])
        for axis in ('xTickColor', 'yTickColor'):
            if graph[axis] is not None:
                self._assert_readable('graph %s axis label' % axis[0], graph[axis], graph['bg'])

    def test_graph_as_the_very_first_view_in_a_second_independent_fresh_context_is_also_readable(self):
        """The graph contrast bar holds when the graph, not the pivot, is the very first view
        opened, in a second independent fresh context (a new `browser_js` call, hence a new
        `ChromeBrowser` profile)."""
        graph_key = 'viin_brand.scheme_first_load_test.graph_only_surfaces'
        code = _wrap(_MEASURE_GRAPH_JS % {'graph_key': graph_key})
        self.browser_js(
            '/odoo/action-%d' % self.graph_action.id, code,
            login=self.dark_user.login, timeout=60,
        )

        graph = self._read_json_param(graph_key)
        self.assertIsNotNone(
            graph['legendColor'],
            "the graph's Chart.js legend produced no items to read a colour from when the graph "
            "was the very first view of a fresh context.",
        )
        self._assert_readable('graph legend (graph-first fresh context)', graph['legendColor'], graph['bg'])
        for axis in ('xTickColor', 'yTickColor'):
            if graph[axis] is not None:
                self._assert_readable(
                    'graph %s axis label (graph-first fresh context)' % axis[0], graph[axis], graph['bg'],
                )
