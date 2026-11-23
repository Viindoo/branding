from lxml import etree

from odoo import api, models

# The button that the lead enrichment service adds to the views of a lead.
ENRICH_BUTTON_NAME = 'iap_enrich'


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if ENRICH_BUTTON_NAME in result['arch']:
            result['arch'] = self._remove_enrich_button(result['arch'])
        return result

    @api.model
    def _remove_enrich_button(self, arch):
        """Return ``arch`` without the enrichment button, and without the header it leaves empty."""
        doc = etree.fromstring(arch)
        for button in doc.xpath('//button[@name="%s"]' % ENRICH_BUTTON_NAME):
            header = button.getparent()
            header.remove(button)
            if header.tag == 'header' and not len(header):
                header.getparent().remove(header)
        return etree.tostring(doc, encoding='unicode')
