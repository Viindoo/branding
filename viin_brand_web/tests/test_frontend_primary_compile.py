# Frontend $primary de-brand guard (PR #658 review-fix C-5; ODOO-AI-ETHOS #8).
#
# WHAT IS PROTECTED (behaviour, not code): on PUBLIC / frontend pages (login, portal), the primary
# CTA + links must render the AA-safe Viindoo teal #007F8E (login "Log in" button, 4.74:1 on white)
# - the flat brand teal #00BBCE fails AA (2.33:1). AND the frontend $primary must be an OVERRIDABLE
# DEFAULT (set with `!default`), so a downstream website `theme_*` that sets its own $primary still
# wins in its recompiled website bundle. The reviewer's caveat: a HARD (non-`!default`) frontend
# $primary hard-overrides every website theme - which the base must not do.
#
# Two mechanisms, two assertion styles:
#  * the RENDERED colour is read from the COMPILED web.assets_frontend bundle (the observable);
#  * `!default` OVERRIDABILITY is a COMPILE-TIME Sass concept that the compiled CSS necessarily
#    ERASES (the pixel is identical whether or not the winning assignment carried `!default`), so it
#    is the ONE thing that can only be asserted at the SCSS source - the base's frontend $primary
#    declaration must carry `!default`. This is the deliberate exception to this cluster's
#    compiled-over-source rule, and it is stated so a future reader does not "upgrade" it to a
#    (impossible) compiled check.
import os
import re

from odoo.tests.common import TransactionCase, tagged

# Compiled-CSS + WCAG helpers are owned by the cascade suite (SSOT); the AA teal constant is owned
# by the brand-colour suite (SSOT). Imported, never re-literalised. Neither of those modules imports
# this one, so there is no import cycle.
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
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand_web/controllers/webmanifest.py (the single Python brand-hex SSOT).",
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
            "The frontend --primary compiled to %s instead of the AA Viindoo teal %s. viin_brand_web "
            "must de-brand the frontend $primary to the AA teal so public pages render on-brand."
            % (frontend_primary, expected_teal),
        )
        self.assertGreaterEqual(
            _contrast_ratio(frontend_primary, WHITE), WCAG_AA_NORMAL_TEXT,
            "The frontend primary %s clears only %.2f:1 against white button text, below the WCAG "
            "AA normal-text threshold of %.1f:1."
            % (frontend_primary, _contrast_ratio(frontend_primary, WHITE), WCAG_AA_NORMAL_TEXT),
        )

    def test_frontend_primary_is_an_overridable_default_not_a_hard_override(self):
        """The base's frontend $primary must be set with `!default` so website themes can win.

        A downstream website `theme_*` sets its own $primary in its recompiled bundle; the base must
        offer the teal as an OVERRIDABLE DEFAULT, not hard-override every theme (the reviewer's
        caveat). `!default` is erased by Sass compilation - the compiled CSS is identical either way
        - so this overridability contract can ONLY be asserted at the SCSS source: the base's
        frontend-reaching $primary declaration MUST carry `!default`. A bare `$primary: <hex>;`
        (no `!default`) is exactly the hard override this guards against."""
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
            "brand_variables.scss declares no `$primary:` - viin_brand_web must own the frontend "
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
