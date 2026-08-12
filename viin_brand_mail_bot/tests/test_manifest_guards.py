# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Manifest guard for the viin_brand_common retirement.

Business rule (viin_brand_common module split - see the sibling guards
``viin_brand_pos/tests/test_manifest_guards.py`` and
``viin_brand_mail/tests/test_install.py`` for the same ``depends``-edge
technique): ``viin_brand_mail_bot`` was audited by direct inspection
(``grep -rn 'viin_brand_common' viin_brand_mail_bot/``) and consumes
NOTHING from ``viin_brand_common`` - no import, no asset path, no SCSS
token read, no template inherit, no xmlid. The only occurrence of
``viin_brand_common`` anywhere in this module was the ``depends`` entry
itself. Because nothing is consumed, the edge is dead weight and is
removed outright, not re-pointed at ``viin_brand_web`` - re-pointing would
just re-create the same dead edge under a new name.

Reading ``ir.module.module.state`` alone cannot protect this rule: another
module in the same database can pull in ``viin_brand_common`` (or
``viin_brand_web``) independently, so the registry could report
"installed" for reasons unrelated to this module's own manifest. The
manifest file is therefore read directly with ``ast.literal_eval`` so the
test is capable of failing for the right reason - the dependency edge
itself.
"""
import ast
import os

from odoo.tests.common import TransactionCase, tagged

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")


def _load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
        return ast.literal_eval(manifest_file.read())


@tagged("post_install", "-at_install")
class TestViinBrandMailBotManifestDependsGuard(TransactionCase):
    """``viin_brand_mail_bot``'s manifest must not depend on ``viin_brand_common``."""

    def test_manifest_does_not_depend_on_viin_brand_common(self):
        manifest = _load_manifest()
        depends = manifest.get("depends", [])
        self.assertNotIn(
            "viin_brand_common", depends,
            "viin_brand_mail_bot/__manifest__.py 'depends' must not declare "
            "viin_brand_common: this module consumes nothing from it (verified by "
            "grep - no import, asset path, SCSS token, template inherit, or xmlid), "
            "so the edge was dead weight and is removed outright rather than "
            "re-pointed at viin_brand_web.",
        )

    def test_manifest_depends_on_mail_bot_and_no_brand_module_at_all(self):
        """MED-1 (integrated review): the assertNotIn above is a NEGATIVE check that will pass
        forever, vacuously, once ``viin_brand_common`` stops existing anywhere in this repo - it
        can never fail again and so stops protecting anything. Assert the POSITIVE invariant it
        was actually meant to protect instead: this module depends on EXACTLY its core counterpart
        (``mail_bot``) and on NO ``viin_brand_*`` module at all - not the retired
        ``viin_brand_common``, not its ``viin_brand_web`` successor, not any future brand module."""
        depends = _load_manifest().get("depends", [])
        self.assertEqual(
            depends, ["mail_bot"],
            "viin_brand_mail_bot must depend on exactly ['mail_bot'] and nothing else: %r"
            % (depends,),
        )
        brand_edges = [entry for entry in depends if entry.startswith("viin_brand")]
        self.assertFalse(
            brand_edges,
            "viin_brand_mail_bot must depend on NO viin_brand_* module (it consumes nothing from "
            "any of them): %r" % (brand_edges,),
        )
