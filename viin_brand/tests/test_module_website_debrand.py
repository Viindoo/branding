import importlib
from urllib.parse import urlparse

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestViinBrandModuleWebsiteDebrand(TransactionCase):
    """The module-website de-brand must stay wired through viin_brand.apriori.

    Regression guard for a silent-fallback bug that already shipped once.
    ``to_base._load_manifest_plus`` (loaded server-wide via
    ``--load base,web,to_base``) overrides EVERY module's manifest ``website``
    with the Viindoo intro/doc URL taken from
    ``odoo.addons.viin_brand.apriori.modules_website`` (resolved by
    ``to_base._get_brand_module_website``). That import lives inside a bare
    ``try/except Exception: pass``, so when ``viin_brand/apriori.py`` was
    mislabeled "dead" and deleted, the override did NOT crash - it silently
    returned ``False`` and every module ``website`` reverted to the stock Odoo
    default, with the whole test suite still green.

    These assertions make that silent regression fail loudly: apriori.py must
    exist and carry a Viindoo URL map (never an odoo.com one), to_base must
    actually consume it, and - end to end - an installed module's stored
    ``website`` must reflect the de-brand.
    """

    def test_apriori_module_website_map_is_present_and_viindoo(self):
        """viin_brand.apriori.modules_website exists and maps only to viindoo.com URLs.

        A missing file or symbol is exactly what the ``except Exception: pass``
        in ``_get_brand_module_website`` swallows, so assert it directly.
        """
        apriori = importlib.import_module('odoo.addons.viin_brand.apriori')
        modules_website = getattr(apriori, 'modules_website', None)
        self.assertIsInstance(
            modules_website, dict,
            "viin_brand/apriori.py must define a `modules_website` dict - "
            "to_base imports it to de-brand every module's website; a missing "
            "file or symbol silently reverts every website to the Odoo default.",
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

    def test_to_base_consumes_apriori_module_website(self):
        """to_base._get_brand_module_website resolves the Viindoo URL from apriori.

        This is the exact function that silently returned ``False`` when
        apriori.py was deleted. A green assertion here proves BOTH that
        apriori.py exists AND that the server-wide to_base patch reads it.
        """
        try:
            from odoo.addons import to_base
        except ImportError:
            self.skipTest(
                "to_base is not importable in this test environment; it must be "
                "loaded server-wide (--load base,web,to_base) for the "
                "module-website de-brand to be active."
            )
        website = to_base._get_brand_module_website('crm')
        self.assertEqual(
            website, 'https://viindoo.com/intro/crm',
            "to_base._get_brand_module_website('crm') returned %r instead of the "
            "Viindoo intro URL. Either viin_brand/apriori.py is missing (its "
            "import in _get_brand_module_website is swallowed by a bare "
            "`except Exception: pass`, silently returning False) or to_base no "
            "longer consumes the apriori map." % (website,),
        )

    def test_installed_module_website_reflects_viindoo_debrand(self):
        """End-to-end: a scanned module's ir.module.module.website is de-branded.

        Proves the FULL pipeline - apriori.modules_website -> to_base
        _load_manifest_plus (patched module._load_manifest) -> manifest scan ->
        ir.module.module.website - not just the resolver in isolation. Defensive:
        checks every apriori-mapped module that has an ir.module.module record on
        this instance, and skips only if none are present (an addons path that
        ships none of the mapped core modules).
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
                "de-brand URL %r from viin_brand.apriori. The to_base "
                "_load_manifest_plus override is not reaching the manifest scan."
                % (module_name, record.website, expected_url),
            )
        if not checked:
            self.skipTest(
                "none of the apriori-mapped modules have an ir.module.module "
                "record on this instance - cannot verify the end-to-end website "
                "de-brand here."
            )
