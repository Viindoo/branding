# Frontend $primary de-brand guard.
#
# On public / frontend pages (login, portal) the primary CTA and links must render the AA-safe
# Viindoo teal #007F8E (login "Log in" button, 4.74:1 on white); the flat brand teal #00BBCE fails
# AA (2.33:1). The frontend $primary must also be an overridable default (`!default`), so a
# downstream website `theme_*` that sets its own $primary still wins in its recompiled bundle.
#
# Two assertion styles:
#  * the rendered colour is read from the compiled web.assets_frontend bundle;
#  * `!default` is a compile-time Sass concept that the compiled CSS erases, so it can only be
#    asserted at the SCSS source: the base's frontend $primary declaration must carry `!default`.
import os
import re

from odoo.tests.common import TransactionCase, tagged

# Compiled-CSS and WCAG helpers come from the cascade suite; the AA teal constant from the
# brand-colour suite.
from .test_brand_cascade_compile import (
    _contrast_ratio,
    _iter_rules,
    _normalize_colour,
    WCAG_AA_NORMAL_TEXT,
    WHITE,
)
from .test_brand_color_compile import VIINDOO_AA_INTERACTIVE_COLOR, VIINDOO_THEME_COLOR
from .test_brand_ssot import BRAND_VARIABLES_SCSS

FRONTEND_BUNDLE = "web.assets_frontend"


@tagged("post_install", "-at_install")
class FrontendPrimaryCompileTest(TransactionCase):

    def _compiled_css(self, bundle_name):
        """Compile an asset bundle by name and return its CSS payload as decoded text."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so the frontend $primary cannot "
            "be verified." % bundle_name,
        )
        return css

    def _root_custom_prop_values(self, css, prop):
        """Values declared for the custom property ``--<prop>`` on a :root rule (last wins)."""
        pattern = re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = []
        for _order, selector, body in _iter_rules(css):
            if selector != ":root":
                continue
            for match in pattern.finditer(body):
                values.append(match.group(1).strip().lower())
        return values

    def test_frontend_primary_renders_the_aa_teal_on_public_pages(self):
        """The frontend primary token must compile to the AA Viindoo teal, never the flat brand teal.

        Read from the COMPILED web.assets_frontend bundle (the observable a login page renders), not
        the SCSS source. The AA teal #007F8E clears WCAG AA on white (4.74:1); the flat brand teal
        #00BBCE fails (2.33:1)."""
        # web.assets_frontend compiles only when html_editor is installed: html_editor defines
        # increase-contrast(), which web/static/src/scss/bootstrap_review_frontend.scss calls
        # unconditionally. Without it the bundle serves the "## CSS error message ##" banner.
        if not self.env["ir.module.module"].search_count(
            [("name", "=", "html_editor"), ("state", "=", "installed")]
        ):
            self.skipTest(
                "html_editor is not installed - web.assets_frontend cannot compile, so there is "
                "no compiled --primary to check."
            )
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        flat_brand_teal = VIINDOO_THEME_COLOR.lower()
        expected_teal = VIINDOO_AA_INTERACTIVE_COLOR

        css = self._compiled_css(FRONTEND_BUNDLE)
        primary_values = [
            c for c in (_normalize_colour(v) for v in self._root_custom_prop_values(css, "primary"))
            if c
        ]
        self.assertTrue(
            primary_values,
            "No concrete :root --primary hex in the compiled web.assets_frontend bundle. The "
            "frontend primary token must resolve to a colour so the login CTA colour can be checked.",
        )
        frontend_primary = primary_values[-1]      # last :root declaration wins
        self.assertNotEqual(
            frontend_primary, flat_brand_teal,
            "The frontend --primary compiled to the flat, WCAG-AA-FAILING brand teal %s. The login "
            "CTA / links need the darker AA teal %s (white button text needs >= 4.5:1)."
            % (flat_brand_teal, expected_teal),
        )
        self.assertEqual(
            frontend_primary, expected_teal,
            "The frontend --primary compiled to %s instead of the AA Viindoo teal %s. viin_brand "
            "must de-brand the frontend $primary to the AA teal so public pages render on-brand."
            % (frontend_primary, expected_teal),
        )
        self.assertGreaterEqual(
            _contrast_ratio(frontend_primary, WHITE), WCAG_AA_NORMAL_TEXT,
            "The frontend primary %s clears only %.2f:1 against white button text, below the WCAG "
            "AA normal-text threshold of %.1f:1."
            % (frontend_primary, _contrast_ratio(frontend_primary, WHITE), WCAG_AA_NORMAL_TEXT),
        )

    def _website_frontend_css(self, website):
        """web.assets_frontend as ``website`` serves it (its own customized files included)."""
        bundle = self.env["ir.qweb"].with_context(website_id=website.id)._get_asset_bundle(
            FRONTEND_BUNDLE, css=True, js=False
        )
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace")
            for attachment in (bundle.css() or self.env["ir.attachment"])
        )
        self.assertTrue(css.strip(), "web.assets_frontend of website %s compiled to empty CSS" % website.id)
        return css

    def _rule_prop(self, css, selector, prop):
        """The last value of the custom property ``--<prop>`` declared on ``selector`` rules."""
        pattern = re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = [
            match.group(1).strip().lower()
            for _order, sel, body in _iter_rules(css) if sel == selector
            for match in pattern.finditer(body)
        ]
        return _normalize_colour(values[-1]) if values else None

    def test_customized_website_palette_keeps_its_own_primary(self):
        """A website whose owner customized its colors keeps its palette's primary and its own
        secondary button colors; a stock website keeps the AA teal.

        A customized o-color-1 (navy #4A6A90 here) must keep driving buttons, links and
        .bg-primary blocks, and a secondary button that set its colour but no border must keep
        Odoo's default border rather than the brand purple border of the stock palette."""
        installed = set(self.env["ir.module.module"].search(
            [("name", "in", ("website", "html_editor")), ("state", "=", "installed")]
        ).mapped("name"))
        if installed != {"website", "html_editor"}:
            self.skipTest("website and html_editor are needed for a website palette to compile")
        website = self.env["website"].search([], order="id", limit=1)
        expected_teal = VIINDOO_AA_INTERACTIVE_COLOR

        stock_css = self._website_frontend_css(website)
        self.assertEqual(
            self._rule_prop(stock_css, ":root", "primary"), expected_teal,
            "A website with the stock palette must keep the AA teal as its frontend primary.",
        )

        navy, white = "#4a6a90", "#ffffff"
        self.env["website.assets"].with_context(website_id=website.id).make_scss_customization(
            "/website/static/src/scss/options/colors/user_color_palette.scss",
            {"o-color-1": navy.upper(), "o-color-5": white.upper(), "o-cc1-btn-secondary": "'o-color-5'"},
        )
        custom_css = self._website_frontend_css(website)
        self.assertEqual(
            self._rule_prop(custom_css, ":root", "primary"), navy,
            "A website whose owner customized its palette must keep the palette's primary (its "
            "o-color-1), not the Viindoo teal.",
        )
        self.assertEqual(
            self._rule_prop(custom_css, ".btn-secondary", "btn-border-color"), white,
            "A customized website that set its own CC1 secondary button but not its border must get "
            "Odoo's default border (the button colour), not the brand purple of the stock palette.",
        )

    def test_frontend_primary_is_an_overridable_default_not_a_hard_override(self):
        """The base's frontend $primary must be set with `!default` so website themes can win.

        A downstream website `theme_*` sets its own $primary in its recompiled bundle; the base must
        offer the teal as an overridable default, not hard-override every theme. `!default` is erased
        by Sass compilation, so this can only be asserted at the SCSS source: a bare
        `$primary: <hex>;` is the hard override this guards against."""
        self.assertTrue(
            os.path.exists(BRAND_VARIABLES_SCSS),
            "brand_variables.scss must exist at %s - it declares the base frontend $primary."
            % BRAND_VARIABLES_SCSS,
        )
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            scss = scss_file.read()
        # Every top-of-line `$primary: <value>;` assignment (ignore `//`-commented lines and the
        # `$primary-...`/`$o-...` neighbours via the exact `$primary:` anchor).
        assignments = re.findall(r"^\s*\$primary\s*:\s*([^;]+);", scss, re.MULTILINE)
        self.assertTrue(
            assignments,
            "brand_variables.scss declares no `$primary:` - viin_brand must own the frontend "
            "primary de-brand (it is contributed to web._assets_primary_variables, which the "
            "frontend bundle includes).",
        )
        for rhs in assignments:
            self.assertIn(
                "!default", rhs,
                "brand_variables.scss sets `$primary: %s;` WITHOUT `!default` - a HARD override that "
                "clobbers every downstream website theme's own $primary. It must be `!default` so "
                "the base offers an OVERRIDABLE teal default." % rhs.strip(),
            )
