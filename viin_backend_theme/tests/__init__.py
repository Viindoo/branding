# -*- coding: utf-8 -*-
# test_theme_prefs was RELOCATED to viin_brand_web/tests/test_color_scheme_pref.py (PR #658
# review-fix C-1): the color-scheme preference field + ir.http.color_scheme() resolver now live in
# the always-installed viin_brand_web, so it owns their behaviour test. Nothing
# theme-specific remained in that file, so it was deleted here rather than trimmed.
# test_w1_substrate was RETIRED (PR #658 review-fix): it asserted the CONTENT of the now-deleted
# no-reload dark_surfaces.scss / scheme.scss (C-2 re-based dark on the recompiled web.assets_web_dark
# bundle). Its surviving real behaviour + the NEW Option-A widget-dark contracts (T-3 stepper marker
# AA, T-4 rail focus ring) live in test_theme_dark_widgets.
# test_theme_button_radius was SUPERSEDED by test_theme_radius_is_core (owner revision 2026-08-03).
# It guarded a two-sided rule that no longer holds - "buttons equal core AND the D13 scale still
# applies to everything else" - because the owner then asked for EVERY radius override to go. Its
# button half survives verbatim as test_buttons_render_odoo_ces_native_radius; its D13 half asserted
# the exact opposite of the current contract, so it was deleted rather than inverted.
# test_theme_core_chrome_untouched is NEW with the owner reverts of 2026-08-03 (D6 statusbar
# stepper, the navbar apps-icon colour override, the D7 stat-button reskin). It is the negative
# counterpart of the files around it: instead of asserting a theme surface looks right, it asserts
# three CORE widgets are left exactly as Odoo CE ships them. The stepper's own Hoot suite
# (static/tests/statusbar_stepper.test.js) and the T-3 dark-marker AA guard were deleted with the
# widget they described - they asserted markup that no longer exists.
from . import test_theme_core_chrome_untouched
from . import test_theme_dark_widgets
# test_home_menu_background is NEW with the owner's 2026-08-03 app-dashboard request. It imports
# test_theme_dark_widgets' :root reader + home-menu element models, so it is listed after it.
from . import test_home_menu_background
from . import test_theme_radius_is_core
from . import test_home_app_order
from . import test_tours
from . import test_manifest_depends
