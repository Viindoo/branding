from lxml import etree

from odoo import api, models

# The buttons and fields that the lead enrichment, lead mining and visitor reveal services add to
# the views of a lead. They are removed from the views, whether or not those modules are installed.
IAP_BUTTON_NAMES = ('iap_enrich', 'action_generate_leads')
IAP_FIELD_NAMES = ('reveal_ip', 'reveal_iap_credits', 'reveal_rule_id')


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        arch = result['arch']
        if any(name in arch for name in IAP_BUTTON_NAMES + IAP_FIELD_NAMES):
            result['arch'] = self._remove_iap_service_nodes(arch)
        return result

    @api.model
    def _remove_iap_service_nodes(self, arch):
        """Return ``arch`` without the buttons and fields of the paid lead services.

        A group left with the reveal fields and a header left with the mining button go with them.
        """
        doc = etree.fromstring(arch)
        for group in doc.xpath('//group[field[@name="reveal_ip"]]'):
            group.getparent().remove(group)
        nodes = doc.xpath('//button[%s]' % ' or '.join('@name="%s"' % name for name in IAP_BUTTON_NAMES))
        nodes += doc.xpath('//field[%s]' % ' or '.join('@name="%s"' % name for name in IAP_FIELD_NAMES))
        for node in nodes:
            parent = node.getparent()
            parent.remove(node)
            if parent.tag == 'header' and not len(parent):
                parent.getparent().remove(parent)
        return etree.tostring(doc, encoding='unicode')
