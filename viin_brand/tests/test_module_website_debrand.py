import importlib
from urllib.parse import urlparse

from odoo.addons.viin_brand import _load_manifest_plus
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestViinBrandModuleWebsiteDebrand(TransactionCase):
    """The module-website de-brand is wired through viin_brand.apriori.

    ``viin_brand._load_manifest_plus`` (loaded server-wide via
    ``--load base,web,viin_brand``) overrides every listed module's manifest ``website``
    with the Viindoo intro/doc URL from
    ``odoo.addons.viin_brand.apriori.modules_website``. These assertions pin that
    ``apriori.py`` carries a Viindoo URL map (never an odoo.com one) and that an
    installed module's stored ``website`` reflects the de-brand.
    """

    def test_apriori_module_website_map_is_present_and_viindoo(self):
        """viin_brand.apriori.modules_website exists and maps only to viindoo.com URLs.

        """
        apriori = importlib.import_module('odoo.addons.viin_brand.apriori')
        modules_website = getattr(apriori, 'modules_website', None)
        self.assertIsInstance(
            modules_website, dict,
            "viin_brand/apriori.py must define a `modules_website` dict - "
            "viin_brand imports it to de-brand every module's website; a "
            "missing file or symbol silently reverts every website to the "
            "Odoo default.",
        )
        self.assertTrue(
            modules_website,
            "viin_brand.apriori.modules_website is empty - the module-website "
            "de-brand would no-op for every module.",
        )
        for module_name, url in modules_website.items():
            parsed = urlparse(url)
            # Parse the host rather than a substring test: `'viindoo.com' in url`
            # is the py/incomplete-url-substring-sanitization pitfall (a host like
            # `viindoo.com.evil.com` would pass). A hostname equality check is exact
            # and also proves the URL is not a stock odoo.com link.
            self.assertEqual(
                parsed.scheme, 'https',
                "modules_website[%r] = %r must be an https URL - the de-brand "
                "sends module websites to Viindoo." % (module_name, url),
            )
            self.assertIn(
                parsed.hostname, ('viindoo.com', 'www.viindoo.com'),
                "modules_website[%r] host = %r, expected a viindoo.com host - the "
                "de-brand must replace the stock odoo.com link." % (module_name, parsed.hostname),
            )

    def test_apriori_maps_crm_to_its_viindoo_intro_page(self):
        """viin_brand.apriori maps the crm module to its Viindoo intro page."""
        apriori = importlib.import_module('odoo.addons.viin_brand.apriori')
        website = apriori.modules_website['crm']
        self.assertEqual(
            website, 'https://viindoo.com/intro/crm',
            "viin_brand.apriori.modules_website['crm'] is %r instead of the Viindoo "
            "intro URL." % (website,),
        )

    def test_installed_module_website_reflects_viindoo_debrand(self):
        """End-to-end: a scanned module's ir.module.module.website is de-branded.

        Covers the whole pipeline - apriori.modules_website ->
        viin_brand._load_manifest_plus -> manifest scan -> ir.module.module.website.
        Checks every apriori-mapped module that has a record on this instance and
        skips only if none are present.
        """
        apriori = importlib.import_module('odoo.addons.viin_brand.apriori')
        modules_website = apriori.modules_website
        module_model = self.env['ir.module.module']
        checked = 0
        for module_name, expected_url in modules_website.items():
            record = module_model.search([('name', '=', module_name)], limit=1)
            if not record:
                continue
            checked += 1
            self.assertEqual(
                record.website, expected_url,
                "ir.module.module %r has website %r, expected the Viindoo "
                "de-brand URL %r from viin_brand.apriori. The "
                "viin_brand._load_manifest_plus override is not reaching the "
                "manifest scan."
                % (module_name, record.website, expected_url),
            )
        if not checked:
            self.skipTest(
                "none of the apriori-mapped modules have an ir.module.module "
                "record on this instance - cannot verify the end-to-end website "
                "de-brand here."
            )

    def test_a_website_that_points_at_odoo_is_emptied_unless_the_module_has_a_viindoo_page(self):
        """An unlisted module whose manifest names odoo.com shows no "Learn more" to Odoo."""
        content = {'depends': ['base'], 'author': 'Test', 'license': 'LGPL-3', 'version': '19.0.1.0'}
        for module_name, website, expected in (
            ('unlisted_odoo', 'https://www.odoo.com/app/sales', ''),
            ('unlisted_odoo_subdomain', 'https://apps.odoo.com/apps/modules/19.0/x', ''),
            ('unlisted_third_party', 'https://example.com/odoo.com', 'https://example.com/odoo.com'),
            ('crm', 'https://www.odoo.com/app/crm', 'https://viindoo.com/intro/crm'),
        ):
            with self.subTest(module=module_name):
                info = _load_manifest_plus(module_name, dict(content, website=website))
                self.assertEqual(info['website'], expected)
