from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHiddenMenusAndBindings(TransactionCase):
    """A branding module hides the menus and the Action menu entries of a service by XML id."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Menu = cls.env['ir.ui.menu']
        action = cls.env['ir.actions.act_window'].create({'name': 'Hide Test', 'res_model': 'res.partner'})
        cls.folder = Menu.create({'name': 'Hide Test Folder'})
        cls.leaf = Menu.create({
            'name': 'Hide Test Leaf', 'parent_id': cls.folder.id, 'action': 'ir.actions.act_window,%d' % action.id,
        })
        cls.other_folder = Menu.create({'name': 'Hide Test Other Folder'})
        cls.other_leaf = Menu.create({
            'name': 'Hide Test Other Leaf', 'parent_id': cls.other_folder.id,
            'action': 'ir.actions.act_window,%d' % action.id,
        })
        cls.model = cls.env['ir.model']._get('res.partner')
        cls.binding = cls.env['ir.actions.server'].create({
            'name': 'Hide Test Binding', 'model_id': cls.model.id, 'binding_model_id': cls.model.id,
            'state': 'code', 'code': 'pass',
        })
        cls.other_binding = cls.binding.copy({'name': 'Hide Test Other Binding'})
        for name, record in (
            ('hide_test_folder', cls.folder), ('hide_test_other_folder', cls.other_folder),
            ('hide_test_binding', cls.binding),
        ):
            cls.env['ir.model.data'].create({
                'module': 'viin_brand', 'name': name, 'model': record._name, 'res_id': record.id,
            })

    def _patch_hidden(self, xmlids):
        Menu = type(self.env['ir.ui.menu'])
        return patch.object(Menu, '_get_hidden_menu_xmlids', lambda self: xmlids)

    def _web_client_menu_ids(self):
        return set(self.env['ir.ui.menu'].load_menus(False)) - {'root'}

    def _load_menu_data(self, xmlid, name):
        values = {'name': name, 'active': True}
        data = {'xml_id': xmlid, 'values': values, 'noupdate': False}
        self.env['ir.ui.menu']._load_records([data], update=True)

    def test_a_listed_menu_leaves_the_web_client_with_the_menus_under_it(self):
        menu_ids = self._web_client_menu_ids()
        self.assertLessEqual({self.folder.id, self.leaf.id}, menu_ids)

        with self._patch_hidden(['viin_brand.hide_test_folder']):
            self.env['ir.ui.menu']._archive_hidden_menus()

        self.assertFalse(self.folder.active)
        self.assertTrue(self.other_folder.active)
        menu_ids = self._web_client_menu_ids()
        self.assertNotIn(self.folder.id, menu_ids)
        self.assertNotIn(self.leaf.id, menu_ids)
        self.assertIn(self.other_leaf.id, menu_ids)

    def test_an_xml_id_that_does_not_resolve_is_ignored(self):
        with self._patch_hidden(['viin_brand.hide_test_absent']):
            self.env['ir.ui.menu']._archive_hidden_menus()

        self.assertTrue(self.folder.active)
        self.assertIn(self.leaf.id, self._web_client_menu_ids())

    def test_loading_the_data_of_a_listed_menu_archives_it_again(self):
        with self._patch_hidden(['viin_brand.hide_test_folder']):
            self.env['ir.ui.menu']._archive_hidden_menus()
            self.folder.active = True
            self.assertTrue(self.folder.active, 'an administrator shows it again')

            self._load_menu_data('viin_brand.hide_test_folder', 'Hide Test Folder')

        self.assertFalse(self.folder.active)

    def test_loading_the_data_of_another_menu_keeps_it_active(self):
        with self._patch_hidden(['viin_brand.hide_test_folder']):
            self._load_menu_data(
                'viin_brand.hide_test_other_folder', 'Hide Test Other Folder',
            )

        self.assertTrue(self.other_folder.active)
        self.assertTrue(self.folder.active)

    def test_restoring_gives_the_menus_back_to_the_web_client(self):
        with self._patch_hidden(['viin_brand.hide_test_folder']):
            self.env['ir.ui.menu']._archive_hidden_menus()

        self.env['ir.ui.menu']._restore_hidden_menus(
            ['viin_brand.hide_test_folder', 'viin_brand.hide_test_absent'],
        )

        self.assertTrue(self.folder.active)
        self.assertIn(self.leaf.id, self._web_client_menu_ids())

    def test_a_listed_action_is_kept_out_of_the_action_menu(self):
        Actions = self.env['ir.actions.actions']
        names = {action['name'] for action in Actions.get_bindings('res.partner').get('action', [])}
        self.assertEqual(names >= {'Hide Test Binding', 'Hide Test Other Binding'}, True)

        with patch.object(
            type(Actions), '_get_hidden_binding_xmlids', lambda self: ['viin_brand.hide_test_binding'],
        ):
            names = {action['name'] for action in Actions.get_bindings('res.partner').get('action', [])}

        self.assertNotIn('Hide Test Binding', names)
        self.assertIn('Hide Test Other Binding', names)

    def test_an_action_xml_id_that_does_not_resolve_is_ignored(self):
        Actions = self.env['ir.actions.actions']
        with patch.object(
            type(Actions), '_get_hidden_binding_xmlids', lambda self: ['viin_brand.hide_test_absent'],
        ):
            names = {action['name'] for action in Actions.get_bindings('res.partner').get('action', [])}

        self.assertIn('Hide Test Binding', names)
