from lxml import etree

from odoo import api, models

# The fields that the visits to leads service adds to the views of a lead.
REVEAL_FIELD_NAMES = ('reveal_ip', 'reveal_iap_credits', 'reveal_rule_id')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if any(name in result['arch'] for name in REVEAL_FIELD_NAMES):
            result['arch'] = self._remove_reveal_fields(result['arch'])
        return result

    @api.model
    def _remove_reveal_fields(self, arch):
        """Return ``arch`` without the reveal fields, and without the group they leave empty."""
        doc = etree.fromstring(arch)
        for group in doc.xpath('//group[field[@name="reveal_ip"]]'):
            group.getparent().remove(group)
        for field in doc.xpath('//field[%s]' % ' or '.join('@name="%s"' % name for name in REVEAL_FIELD_NAMES)):
            field.getparent().remove(field)
        return etree.tostring(doc, encoding='unicode')
