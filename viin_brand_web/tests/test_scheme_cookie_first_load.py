# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): a dark-preference user's very FIRST page load of a
# brand-new browser session must already be dark end-to-end - the webclient response itself, and
# every lazy-loaded view bundle it triggers. Two mechanisms are guarded here:
#
#   B0 - `ir.http`'s webclient-rendering hook must WRITE the resolved `color_scheme` onto the
#   RESPONSE (`request.future_response.set_cookie('color_scheme', <scheme>)`) whenever it differs
#   from the request's own incoming cookie value, and must NOT re-emit it once the two already
#   match. `color_scheme()`'s own resolution precedence (cookie > stored preference > super()) is
#   UNCHANGED by this - that precedence is guarded by tests/test_color_scheme_pref.py, which stays
#   untouched.
#
#   The reachability problem B0 fixes: `web/static/src/views/view.js:348-352` decides whether to
#   `loadBundle("web.assets_backend_lazy_dark")` or the light sibling by reading
#   `cookie.get("color_scheme")` - a synchronous browser-cookie read, not an RPC. On a session that
#   has NEVER received a `color_scheme` cookie, that read is empty even for a user whose STORED
#   preference is dark, so the very first pivot/graph opened in that session can still load the
#   LIGHT lazy bundle. Worse, `web/static/src/views/graph/graph_renderer.js:29-32` reads the same
#   cookie into a MODULE-LEVEL constant (`const colorScheme = cookie.get("color_scheme")`), which
#   is evaluated exactly ONCE per session (ES modules are cached) - so whichever scheme is in the
#   cookie the first time that module loads freezes the chart's legend/axis colours for the whole
#   session. Odoo's own `ir.http.webclient_rendering_context()` (`web/models/ir_http.py:71-75`)
#   already calls `self.color_scheme()` before rendering `web.webclient_bootstrap` for every
#   `/odoo` request (`web/controllers/home.py:69-76`); B0 rides that exact same call to make the
#   cookie arrive WITH the very first HTML response, before any lazy bundle or JS module ever asks.
#
# WHY THIS IS AN HttpCase, NOT A COMPILED-CSS CHECK: the defect is entirely about WHEN a cookie
# exists relative to WHEN a browser evaluates JS that reads it once - no amount of resolving SCSS
# can observe a race between an HTTP response header and a module-level `const`. Every colour
# below is read straight out of the live browser: `getComputedStyle` for the pivot's rendered text
# and its effective background, and the graph's OWN Chart.js instance (`window.Chart.getChart`)
# for the legend/axis colours it configured - never re-derived from a stylesheet.
#
# WHY EACH `browser_js` / `start_tour` CALL IS ALREADY "A FRESH CONTEXT" WITH NO ACT OF INJECTION:
# `HttpCase.browser_js` (`odoo/tests/common.py:2464-2497`) creates a brand-new `ChromeBrowser` per
# call, and `ChromeBrowser.__init__` gives it its OWN throwaway `--user-data-dir` (a fresh
# `tempfile.TemporaryDirectory`, cleaned up on exit) - so two separate calls can never share a
# cookie jar. `HttpCase.authenticate(..., browser=browser)` (:2372-2432), which every `browser_js`
# call runs internally, seeds ONLY the `session_id` cookie on that fresh browser - never
# `color_scheme`. So simply calling `browser_js`/`start_tour` a second time already IS "a second,
# independent fresh context" - no cookie is ever manually seeded to engineer that.
import json

from odoo.tests import HttpCase, new_test_user, tagged

# WCAG contrast machinery is owned by the compiled-CSS cascade suite (SSOT); imported, never
# re-implemented here. `_normalize_colour` already accepts both `#rrggbb` and the `rgb()`/`rgba()`
# strings `getComputedStyle` returns, which is exactly the shape every value below arrives in.
from .test_brand_cascade_compile import (
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _normalize_colour,
)

# JS helpers shared by every browser_js call below: a JSON-RPC `ir.config_parameter.set_param`
# (the only channel that can round-trip a measured value back to this test's own transaction - see
# `_read_json_param`), a generic poll-until-truthy waiter (the webclient mounts views
# asynchronously; a tour `trigger` is not usable here because the measurement itself, not just the
# wait, has to run as plain JS - see the module docstring on why this cannot be a static tour
# file), and an "effective background" walk (the element under test is not always the one that
# paints the surface a user perceives behind its text - a transparent ancestor must be skipped).
_JS_HELPERS = """
async function __setParam(key, value) {
    const resp = await fetch('/web/dataset/call_kw/ir.config_parameter/set_param', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {model: 'ir.config_parameter', method: 'set_param', args: [key, value], kwargs: {}},
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
    throw new Error('__waitFor: timed out waiting for a condition');
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

# Measures a pivot value cell's text colour and its own effective background, then reports the
# pair under `key`. `.o_pivot_cell_value .o_value` is the text-carrying node core renders for any
# non-boolean measure (web/static/src/views/pivot/pivot_renderer.xml); the value's own `<td>`
# ancestor is what carries the `bg-100` surface class, so the background is read from THAT element
# via `__effectiveBackground`, not the inner text node.
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

# Measures the graph's live Chart.js instance - never a stylesheet - for the legend swatch colour
# (`chart.legend.legendItems[i].fontColor`, the exact field Chart.js's own renderer paints the
# legend text with: web/static/lib/Chart/Chart.js `ctx.fillStyle = legendItem.fontColor`) and the
# x/y axis tick colour (`chart.options.scales.<axis>.ticks.color`, the declarative option
# `graph_renderer.js:559-586` sets directly - Chart.js resolves it verbatim with no per-item
# transform, unlike the legend). `window.Chart` is the vendored UMD global
# (web/static/lib/Chart/Chart.js: `window.Chart = Chart`), and `Chart.getChart(canvas)` is its
# public API for recovering the live instance mounted on a given `<canvas>`.
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
    """Wrap a measurement snippet in the throw/console.error contract `HttpCase.browser_js` polls
    for (`console.log('test successful')` on success, `console.error` on any thrown failure)."""
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
    """`ir.http`'s webclient-rendering hook writes the resolved colour scheme onto the RESPONSE
    cookie exactly when it disagrees with the request's own cookie, and never rewrites it once the
    two already agree."""

    def test_response_cookie_converges_to_the_resolved_scheme_and_then_stays_stable(self):
        """A dark-preference user with no `color_scheme` cookie yet gets one written on their very
        first response; a second request, now carrying that cookie, gets no further Set-Cookie for
        it.

        Both halves are asserted in ONE test, in this order, on purpose: idempotency ("no rewrite
        once it already matches") is only a meaningful claim once the cookie has genuinely
        converged, and a fresh session with no `color_scheme` cookie at all cannot exercise the
        "already matches" branch on its own - manufacturing a matching cookie by hand rather than
        by the mechanism's own first response would prove nothing about THIS mechanism. Driving
        both requests through the SAME `requests.Session`-backed opener lets the second leg pick
        up the first response's Set-Cookie the way a real browser would.
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
            "self.color_scheme(), which already resolves 'dark' from the stored preference; the "
            "response itself must carry that resolution so the very first lazy pivot/graph bundle "
            "sees it without racing an RPC.",
        )

        second = self.url_open('/odoo')
        self.assertNotIn(
            'color_scheme', second.cookies,
            "a second request whose incoming color_scheme cookie already equals the resolved "
            "scheme must not receive another Set-Cookie for it - the write is a convergence, not "
            "an every-request re-assertion.",
        )

    def _rpc_write(self, model, res_id, vals):
        # The RPC channel a real Preferences-form save goes through - res.users.write() must run
        # INSIDE this same request's dispatch for request.future_response to exist at all (a bare
        # self.env[...].write() call from Python has no bound request), and Dispatcher.post_dispatch
        # (odoo/http.py) injects future_response's cookies into the final HTTP response for every
        # route kind, JSON-RPC included - so this is the only channel that can observe the claim.
        response = self.url_open('/web/dataset/call_kw/%s/write' % model, json={
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {'model': model, 'method': 'write', 'args': [[res_id], vals], 'kwargs': {}},
        })
        result = response.json()
        self.assertNotIn('error', result, result.get('error'))
        return response

    def test_response_cookie_syncs_when_a_user_writes_their_own_color_scheme_to_light_or_dark(self):
        """Writing one's OWN `viin_color_scheme` to `light` or `dark` must sync the `color_scheme`
        response cookie in that SAME response - otherwise a user who already carries the OPPOSITE
        value from an earlier session sees no effect from the change until that cookie's own
        year-long expiry. With no write() override at all, a bare `super().write(vals)` cannot
        possibly emit this header for either value."""
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
        """The sync is scoped to the ACTING user's own preference change, mirroring this model's
        existing SELF_WRITEABLE_FIELDS boundary (a user's own field write pins to that user;
        writing someone else's record falls outside that scope) - an admin changing a DIFFERENT
        user's preference must not have that write bleed into the admin's OWN response cookie."""
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
        """Switching one's OWN `viin_color_scheme` to `auto` ("System") must NOT touch the
        `color_scheme` cookie.

        Under 'auto' that cookie is the only place the resolved scheme exists: the server cannot
        read the device preference, so the client resolves it, writes the effective light|dark
        there, and only then issues this write. Expiring it here would discard the answer for the
        reload that immediately follows - the server would serve core's 'light' whatever the
        device says - and would also blank the value core's own dark-mode clients read (graph
        colours, the colour picker, the ace editor, the pdf.js viewer)."""
        user = new_test_user(
            self.env, login='viin_scheme_cookie_auto_keep', groups='base.group_user',
            viin_color_scheme='dark',
        )
        self.authenticate(user.login, user.login)

        # Arrange: the browser already carries a resolved scheme, which is the state a real
        # setScheme('auto') reaches before awaiting this write.
        pinned = self._rpc_write('res.users', user.id, {'viin_color_scheme': 'dark'})
        self.assertEqual(
            pinned.cookies.get('color_scheme'), 'dark',
            "premise broken: the browser was never carrying a resolved scheme, so this test "
            "could not observe whether switching to auto preserves one.",
        )

        response = self._rpc_write('res.users', user.id, {'viin_color_scheme': 'auto'})
        # `response.cookies` drops an expired cookie once processed, and `response.headers`
        # collapses repeated same-name headers down to the last one seen - neither would reveal an
        # EXPIRING Set-Cookie. Read the raw header list, the way `FutureResponse.set_cookie`
        # (odoo/http.py) emits it.
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
    a `color_scheme` cookie, must already render with readable (WCAG AA, >= 4.5:1) text - not the
    light lazy bundle a cookie-less first load can otherwise ship.

    The pivot/graph action lives entirely inside viin_brand_web's OWN install-dependency closure
    (base, web, base_setup, viin_brand - viin_brand/__manifest__.py depends only those three): a
    throwaway pivot and a throwaway graph view on `res.partner`, created in this test's own
    transaction, never `sale` or any addon outside that closure.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Enough records for the pivot/graph "Total" aggregation to have data at all
        # (model.hasData()) - no groupby needed, Count is the always-available default measure.
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
            'arch': '<graph/>',
        })
        cls.graph_action = cls.env['ir.actions.act_window'].create({
            'name': 'Dark Mode First Load Graph (test)',
            'res_model': 'res.partner',
            'view_mode': 'graph',
            'view_id': cls.graph_view.id,
        })
        # A Settings-level user only because measuring needs to round-trip a value through
        # ir.config_parameter.set_param, which base's own ir.model.access.csv restricts to
        # base.group_system - the dark-preference behaviour under test has nothing to do with
        # that group, it is only the measurement channel's own requirement.
        cls.dark_user = new_test_user(
            cls.env, login='viin_fresh_dark_first_load',
            groups='base.group_user,base.group_system',
            viin_color_scheme='dark',
        )

    def setUp(self):
        super().setUp()
        # Isolate B0 from a SECOND, independent client-side cookie writer: viin_backend_theme's
        # own viinThemeService (viin_backend_theme/static/src/webclient/viin_theme_service.js)
        # ALSO sets the `color_scheme` cookie on every webclient boot, unconditionally, once its
        # own `orm.read` resolves - a lightweight single-record read that frequently (not always)
        # wins the very race B0 exists to remove, since it starts as soon as ROOT SERVICES boot,
        # before the heavier action/view-loading chain reaches a lazy bundle's module evaluation.
        # Left in place, this test would measure whichever of the two async operations happened
        # to finish first in a given run - a coin flip, not a repeatable proof of B0.
        #
        # Both the service AND its one production consumer (ViinAppearanceSystray - the ONLY
        # `useService("viin_theme")` call site: appearance_systray.js/.xml/.scss, confirmed by
        # grepping every static/ tree across this module set) are removed from `web.assets_backend`
        # together - removing only the service leaves a dangling `useService("viin_theme")` in
        # the still-loaded systray widget, which throws an OwlError and breaks the whole page
        # (a broken measurement, not a RED). Neither file is needed for the pivot/graph surfaces
        # under test - it is a navbar dropdown icon, not part of any view. `bootEffective`
        # (root.dataset.bsTheme, stamped by the SERVER-rendered boot template regardless of this
        # service) is what keeps the surrounding page chrome correctly dark either way - only the
        # confounding client-side cookie WRITE is neutralised. Both rows are transient, rolled
        # back with the test transaction like any other record this test creates.
        if self.env['ir.module.module']._get('viin_backend_theme').state == 'installed':
            assets = self.env['ir.asset'].sudo().create([
                {
                    'name': 'Neutralise viin_theme_service cookie write (scheme first-load test)',
                    'bundle': 'web.assets_backend',
                    'directive': 'remove',
                    'path': 'viin_backend_theme/static/src/webclient/viin_theme_service.js',
                },
                {
                    'name': 'Neutralise viin_theme_service\'s only consumer (scheme first-load test)',
                    'bundle': 'web.assets_backend',
                    'directive': 'remove',
                    'path': 'viin_backend_theme/static/src/webclient/appearance_systray/**/*',
                },
            ])
            self.addCleanup(assets.sudo().unlink)
            self.addCleanup(self.env.registry.clear_cache, 'assets')

    def _read_json_param(self, key):
        # The browser's requests run on a different test cursor than self.env's own (same
        # transaction, separate cache) - invalidate before reading back what it wrote.
        self.env.invalidate_all()
        raw = self.env['ir.config_parameter'].sudo().get_param(key)
        self.assertTrue(
            raw,
            "premise broken: the browser-side measurement never reported a value under %r - the "
            "page must not have reached the surface under test" % key,
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
        pivot_key = 'viin_brand_web.scheme_first_load_test.pivot_surfaces'
        graph_key = 'viin_brand_web.scheme_first_load_test.graph_surfaces'
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
        """The SAME graph-first-load contrast bar holds when the graph, not the pivot, is
        deliberately the very first view opened - in a SECOND, wholly independent fresh context
        (a brand-new `browser_js` call, hence a brand-new `ChromeBrowser` profile - see the module
        docstring on why this needs no manual cookie seeding at all)."""
        graph_key = 'viin_brand_web.scheme_first_load_test.graph_only_surfaces'
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
