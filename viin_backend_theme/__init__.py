# -*- coding: utf-8 -*-
# The res.users.viin_color_scheme preference and the ir.http.color_scheme resolution live in the
# always-installed viin_brand_web (reached here via 'depends'), so dark mode works even
# without this redesign theme. This theme owns ONE server-side field of its own: the per-user
# home-menu app order (res.users.viin_home_app_order, PR #658 item 7), whose sole consumer is the
# theme's flat home menu - hence models/ lives here, not in the base.
from . import models
