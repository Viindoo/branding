{
    'name': "Viindoo Branding",
    'name_vi_VN': "Ứng dụng với thương hiệu Viindoo",

    'summary': """
Set Viindoo Brandings.
""",

    'summary_vi_VN': """
Thiết lập thương hiệu Viindoo.
        """,

    'description': """
This module replaces the Odoo branding of the base, web and base_setup modules with Viindoo's

* Replace Odoo's module icons and favicon with Viindoo's

  * icons live in `viin_brand/static/img/apps/<module_name>.png`, or in a
    module named `viin_brand_<module_name>` shipping `static/description/icon.png`
  * the favicon lives in `viin_brand/static/img/favicon.ico` and is applied to every company
  * load the module server wide (`--load=base,web,viin_brand`) so the branding
    is in place from the first module installation

* Show Viindoo identity on every page, dialog and document

  * the database manager, the login page, the browser tab title, the report layouts and the
    offline page carry the Viindoo name, logo and links
  * the web app manifest carries the Viindoo name, colour and icons
  * dialogs and error dialogs carry the Viindoo name, and documentation links point to Viindoo's
    documentation

* Let every user choose a Light, Dark or System color scheme in their Preferences, with the
  Viindoo brand palette in both schemes

* Do not bother users with Enterprise-only offers

  * the Apps lists hide the Enterprise modules that are not available in Viindoo, the categories
    and filters that only offer them, and the apps store of Odoo
  * the Settings page hides the options that need Enterprise or a module that cannot be installed,
    and the blocks and apps left empty
  * the modules that sell Odoo IAP credits are not installed with a new database and cannot be
    installed from the user interface; they still install from the command line or as a dependency
    of another module, and a database that has them keeps them


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô đun này thay thương hiệu Odoo của các mô đun base, web và base_setup bằng thương hiệu Viindoo

* Thay biểu tượng mô-đun và favicon của Odoo bằng của Viindoo

  * biểu tượng nằm ở `viin_brand/static/img/apps/<tên_mô_đun>.png`, hoặc ở mô-đun
    `viin_brand_<tên_mô_đun>` có `static/description/icon.png`
  * favicon nằm ở `viin_brand/static/img/favicon.ico` và được áp cho mọi công ty
  * nạp mô-đun ở chế độ toàn máy chủ (`--load=base,web,viin_brand`) để thương hiệu có ngay từ lần
    cài mô-đun đầu tiên

* Hiện nhận diện Viindoo trên mọi trang, hộp thoại và tài liệu

  * trang quản lý cơ sở dữ liệu, trang đăng nhập, tiêu đề thẻ trình duyệt, mẫu báo cáo và trang
    ngoại tuyến mang tên, logo và liên kết của Viindoo
  * tệp kê khai ứng dụng web mang tên, màu và biểu tượng của Viindoo
  * hộp thoại và hộp thoại lỗi mang tên Viindoo, liên kết tài liệu trỏ tới tài liệu của Viindoo

* Cho mỗi người dùng chọn giao diện Sáng, Tối hoặc Hệ thống trong Tùy chọn, với bảng màu thương
  hiệu Viindoo ở cả hai giao diện

* Không làm phiền người dùng bằng các chào mời của ấn bản Enterprise

  * Danh sách Ứng dụng ẩn các mô-đun Enterprise không có sẵn trong Viindoo, các danh mục và bộ lọc
    chỉ dành cho chúng, và kho ứng dụng của Odoo
  * Trang Cài đặt ẩn các tùy chọn cần Enterprise hoặc cần mô-đun không thể cài đặt,
    cùng các khối và ứng dụng bị bỏ trống
  * Các mô-đun bán credit Odoo IAP không được cài cùng cơ sở dữ liệu mới và không thể cài đặt từ
    giao diện người dùng; chúng vẫn được cài từ dòng lệnh hoặc khi là phụ thuộc của mô-đun khác,
    và cơ sở dữ liệu đã có chúng thì giữ nguyên

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.3.3',
    # 'web' is needed at load time: controllers/database.py and controllers/webmanifest.py subclass
    # the core controllers. 'base_setup' is the parent of views/res_config_settings_views.xml.
    'depends': ['base', 'web', 'base_setup'],
    'data': [
        'data/viin_brand_data.xml',
        'data/res_company_data.xml',
        'data/res_partner_data.xml',
        'data/ir_actions_data.xml',
        'views/base_wizard_views.xml',
        'views/ir_module_views.xml',
        'views/ir_ui_view_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/webclient_templates.xml',
        'views/report_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand/static/src/scss/brand_variables.scss'),
            # Appended, not anchored: it must run after html_editor's variables, which build
            # $o-color-palettes, whichever of the two modules loads first.
            'viin_brand/static/src/scss/brand_palette_reset.scss',
        ],
        'web.assets_web_dark': [
            # The dark palette lands before core consumes the Sass variables, so every core rule
            # recompiles dark-correct.
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand/static/src/scss/dark_palette.scss'),
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand/static/src/scss/dark_invariant_pins.scss'),
            # After the `*-dark` tokens it reads, before the maps built from them.
            ('after', 'web/static/lib/bootstrap/scss/_variables-dark.scss',
             'viin_brand/static/src/scss/dark_theme_tints.scss'),
            ('after', 'web/static/src/webclient/webclient.scss',
             'viin_brand/static/src/scss/dark_badge_label.scss'),
            # After core's primary_variables.scss, where the active-state tokens it forwards exist.
            ('after', 'web/static/src/scss/primary_variables.scss',
             'viin_brand/static/src/scss/dark_buttons.scss'),
            # Listed explicitly: core's `*.dark.scss` glob covers only its own tree.
            'viin_brand/static/src/scss/dark_secondary_surfaces.dark.scss',
        ],
        'web.assets_backend_lazy_dark': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand/static/src/scss/dark_palette.scss'),
            ('after', 'web/static/lib/bootstrap/scss/_variables-dark.scss',
             'viin_brand/static/src/scss/dark_theme_tints.scss'),
        ],
        'web.assets_frontend': [
            # After pre_variables.scss, where html_editor's palette-derived primary otherwise wins.
            ('after', 'web/static/src/scss/pre_variables.scss',
             'viin_brand/static/src/scss/frontend_primary.scss'),
            # Re-registers core's keys with `force`, so it must load after core's registration.
            'viin_brand/static/src/core/errors/error_notifications.js',
            # The scoped-app install page loads no backend bundle.
            'viin_brand/static/src/core/install_scoped_app/install_scoped_app.xml',
            # Dialogs, errors and the page title of the website, the portal and the public pages.
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
            'viin_brand/static/src/core/browser/title_service.js',
        ],
        'web.assets_backend': [
            'viin_brand/static/src/webclient/webclient.js',
            'viin_brand/static/src/webclient/settings_form_view/settings/settings_page.js',
            'viin_brand/static/src/webclient/settings_form_view/settings/settings_page.xml',
            'viin_brand/static/src/webclient/settings_form_view/widgets/res_config_edition.xml',
            'viin_brand/static/src/webclient/user_menu_item.js',
            'viin_brand/static/src/webclient/actions/action_dialog.js',
            'viin_brand/static/src/webclient/actions/reports/report_notification.js',
            'viin_brand/static/src/core/barcode/barcode_video_scanner.js',
            'viin_brand/static/src/core/dialog/dialog.js',
            # Text links take the brand secondary; buttons and tabs keep the interactive teal.
            # Anchored between core's `$link-color` and Bootstrap's derived link variables.
            ('before', 'web/static/lib/bootstrap/scss/_variables.scss',
             'viin_brand/static/src/scss/link_tier.scss'),
            # Bootstrap's `$purple` is the Viindoo purple in the backend only; it must be set before
            # pre_variables.scss builds the colour map from it.
            ('before', 'web/static/src/scss/pre_variables.scss',
             'viin_brand/static/src/scss/backend_variables.scss'),
            'viin_brand/static/src/scss/focus_ring.scss',
            'viin_brand/static/src/scss/color_scheme.scss',
            # Anchored: its `.o_progressbar .o_progress` rule ties core's on specificity and wins on
            # source position.
            ('after', 'web/static/src/views/fields/progress_bar/progress_bar_field.scss',
             'viin_brand/static/src/scss/brand_cascade.scss'),
            # Eager: reassigns core's colour exports before the lazy graph and pivot views snapshot them.
            'viin_brand/static/src/core/colors/colors.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
            'viin_brand/static/src/core/browser/title_service.js',
            'viin_brand/static/src/views/widgets/**/*',
            'viin_brand/static/src/views/fields/statusbar/statusbar_steps.js',
            'viin_brand/static/src/views/fields/statusbar/statusbar_steps.xml',
            'viin_brand/static/src/views/fields/statusbar/statusbar_steps.scss',
            # Anchored after the core file each one restyles: the selectors tie core's on
            # specificity and win on source position, and a renamed core file fails the bundle.
            ('after', 'web/static/src/core/commands/command_palette.scss',
             'viin_brand/static/src/core/commands/command_palette.scss'),
            ('after', 'web/static/src/core/dialog/dialog.scss',
             'viin_brand/static/src/core/dialog/dialog.scss'),
            ('after', 'web/static/src/core/dropdown/dropdown.scss',
             'viin_brand/static/src/core/dropdown/dropdown.scss'),
            ('after', 'web/static/src/core/notebook/notebook.scss',
             'viin_brand/static/src/core/notebook/notebook.scss'),
            ('after', 'web/static/src/core/notifications/notification.scss',
             'viin_brand/static/src/core/notifications/notification.scss'),
            ('after', 'web/static/src/core/popover/popover.scss',
             'viin_brand/static/src/core/popover/popover.scss'),
            ('after', 'web/static/src/core/tooltip/tooltip.scss',
             'viin_brand/static/src/core/tooltip/tooltip.scss'),
            ('after', 'web/static/src/core/ui/block_ui.scss',
             'viin_brand/static/src/core/ui/block_ui.scss'),
            ('after', 'web/static/src/search/control_panel/control_panel.scss',
             'viin_brand/static/src/search/control_panel/control_panel.scss'),
            ('after', 'web/static/src/webclient/loading_indicator/loading_indicator.scss',
             'viin_brand/static/src/webclient/loading_indicator/loading_indicator.scss'),
            ('after', 'web/static/src/views/kanban/kanban_record.scss',
             'viin_brand/static/src/views/kanban/kanban_record.scss'),
            ('after', 'web/static/src/views/list/list_renderer.scss',
             'viin_brand/static/src/views/list/list_renderer.scss'),
            ('after', 'web/static/src/views/view_components/selection_box.scss',
             'viin_brand/static/src/views/view_components/selection_box.scss'),
            # Extends core's web.SelectionBox template, so it only shares a bundle with it.
            'viin_brand/static/src/views/view_components/selection_box.xml',
            ('after', 'web/static/src/views/view.scss',
             'viin_brand/static/src/views/view.scss'),
        ],
        'web.assets_unit_tests': [
            'viin_brand/static/tests/dialog_debrand.test.js',
            'viin_brand/static/tests/action_dialog_debrand.test.js',
            'viin_brand/static/tests/barcode_video_scanner_debrand.test.js',
            'viin_brand/static/tests/documentation_link_debrand.test.js',
            'viin_brand/static/tests/user_menu_debrand.test.js',
            'viin_brand/static/tests/colors_debrand.test.js',
            'viin_brand/static/tests/statusbar_steps.test.js',
            'viin_brand/static/tests/error_dialogs_debrand.test.js',
            'viin_brand/static/tests/notification_alert_debrand.test.js',
            'viin_brand/static/tests/report_notification_debrand.test.js',
            'viin_brand/static/tests/title_service_debrand.test.js',
        ],
        'web.assets_tests': [
            'viin_brand/static/tests/tours/about_debrand_tour.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'post_load': 'post_load',
    'installable': True,
    # Installing `web` installs the branding, which in turn pulls the other branding modules in.
    'auto_install': ['web'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
