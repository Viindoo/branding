import base64
import io
import re
from unittest.mock import patch

from lxml import etree

from odoo import fields
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import pdf

from odoo.addons.base.tests.files import PDF_RAW

METADATA_TEMPLATE = 'account_edi_ubl_cii.account_invoice_pdfa_3_facturx_metadata'
GENERATED_REPORT = 'account_edi_ubl_cii.action_report_account_invoices_generated_by_odoo'
GENERATED_LAYOUT = 'account_edi_ubl_cii.layout_invoices_generated_by_odoo'
ODOO_PURPLE = '#714B67'
VIINDOO_PURPLE = '#7F4282'
NS = {
    'pdfaid': 'http://www.aiim.org/pdfa/ns/id/',
    'pdfaExtension': 'http://www.aiim.org/pdfa/ns/extension/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'pdf': 'http://ns.adobe.com/pdf/1.3/',
    'xmp': 'http://ns.adobe.com/xap/1.0/',
}


@tagged('post_install', '-at_install')
class TestFacturxMetadata(TransactionCase):
    """A Factur-X PDF/A-3 document names Viindoo, in its document information and in its XMP."""

    def _facturx_pdf(self):
        """Build the PDF as the invoice sending does: PDF/A conversion, then the rendered XMP."""
        xmp = self.env['ir.qweb']._render(
            METADATA_TEMPLATE,
            {'title': 'INV/2026/00001', 'date': fields.Date.context_today(self.env.user)},
        )
        writer = pdf.OdooPdfFileWriter()
        writer.clone_reader_document_root(pdf.OdooPdfFileReader(io.BytesIO(PDF_RAW), strict=False))
        writer.convert_to_pdfa()
        writer.add_file_metadata(str(xmp).encode())
        buffer = io.BytesIO()
        writer.write(buffer)
        reader = pdf.OdooPdfFileReader(io.BytesIO(buffer.getvalue()), strict=False)
        info = reader.metadata
        packet = reader.trailer['/Root']['/Metadata'].get_object().get_data()
        return info, etree.fromstring(re.sub(rb'<\?xpacket[^>]*\?>', b'', packet))

    def test_document_information_and_xmp_agree_on_viindoo(self):
        info, xmp = self._facturx_pdf()

        self.assertEqual((info['/Creator'], info['/Producer']), ('Viindoo', 'Viindoo'))
        self.assertEqual(xmp.findtext('.//xmp:CreatorTool', namespaces=NS), info['/Creator'])
        self.assertEqual(xmp.findtext('.//pdf:Producer', namespaces=NS), info['/Producer'])

    def test_xmp_names_no_odoo(self):
        _info, xmp = self._facturx_pdf()

        texts = [text.strip() for text in xmp.itertext() if text.strip()]
        self.assertIn('Viindoo', xmp.findtext('.//dc:description//{*}li', namespaces=NS))
        self.assertFalse([text for text in texts if re.search(r'\bOdoo\b', text)])

    def test_xmp_keeps_the_invoice_title_and_the_pdfa_and_facturx_parts(self):
        _info, xmp = self._facturx_pdf()

        self.assertEqual(xmp.findtext('.//dc:title//{*}li', namespaces=NS), 'INV/2026/00001')
        self.assertEqual(xmp.findtext('.//pdfaid:part', namespaces=NS), '3')
        self.assertEqual(xmp.findtext('.//pdfaid:conformance', namespaces=NS), 'A')
        self.assertTrue(xmp.findall('.//pdfaExtension:schemas', NS))
        self.assertIn('urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#', etree.tostring(xmp, encoding='unicode'))


@tagged('post_install', '-at_install')
class TestGeneratedInvoiceReport(TransactionCase):

    def test_report_action_name_names_viindoo_not_odoo(self):
        name = self.env.ref(GENERATED_REPORT).name
        self.assertNotRegex(name, r'\bOdoo\b')
        self.assertIn('Viindoo', name)

    def test_preview_badge_of_the_generated_report_is_not_odoo_purple(self):
        layout = self.env.ref(GENERATED_LAYOUT)._get_combined_arch()
        badges = layout.xpath('//div[contains(@style, "%s")]' % VIINDOO_PURPLE)
        self.assertEqual(len(badges), 1)
        odoo_purple_users = layout.xpath(
            '//*[contains(translate(@style, "ABCDEF", "abcdef"), "%s")]' % ODOO_PURPLE.lower())
        self.assertFalse(odoo_purple_users)


@tagged('post_install', '-at_install')
class TestGeneratedPdfName(TransactionCase):
    """Only the PDF this database generates for a vendor bill is named after Viindoo."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move = cls.env['account.move'].create({'move_type': 'in_invoice'})
        cls.common = cls.env['account.edi.common']

    def _generate_substitute_pdf(self):
        """Run the import step that renders and attaches the substitute PDF of a vendor bill."""
        report = self.env.registry['ir.actions.report']
        with patch.object(report, '_render_qweb_pdf', return_value=(PDF_RAW, 'pdf')):
            return self.common._generate_pdf_attachment(self.move, etree.fromstring('<Invoice/>'))

    def _import_embedded_pdf(self, sender_name):
        """Run the import step that attaches the PDF a received XML document embeds."""
        xml = (
            '<Invoice xmlns:cac="urn:cac" xmlns:cbc="urn:cbc"><cac:AdditionalDocumentReference>'
            '<cbc:ID>%s</cbc:ID><cac:Attachment>'
            '<cbc:EmbeddedDocumentBinaryObject mimeCode="application/pdf">%s</cbc:EmbeddedDocumentBinaryObject>'
            '</cac:Attachment></cac:AdditionalDocumentReference></Invoice>'
        ) % (sender_name, base64.b64encode(PDF_RAW).decode())
        return self.common._import_attachments(self.move, etree.fromstring(xml))

    def _attachment(self, name, **vals):
        values = {
            'name': name,
            'res_model': 'account.move',
            'res_id': self.move.id,
            'raw': PDF_RAW,
            'mimetype': 'application/pdf',
        }
        values.update(vals)
        return self.env['ir.attachment'].create(values)

    def test_substitute_pdf_name_names_viindoo_not_odoo(self):
        attachment = self._generate_substitute_pdf()
        self.assertEqual(attachment.res_id, self.move.id)
        self.assertNotRegex(attachment.name, r'\bOdoo\b')
        self.assertIn('Viindoo', attachment.name)

    def test_pdf_embedded_in_a_received_document_keeps_the_name_of_its_sender(self):
        attachment = self._import_embedded_pdf('VENDOR-0042 - Generated by Odoo.pdf')
        self.assertEqual(attachment.name, 'VENDOR-0042 - Generated by Odoo.pdf')

    def test_pdf_named_after_the_substitute_of_another_bill_keeps_its_name(self):
        attachment = self._attachment('VENDOR-0042 - Generated by Odoo.pdf')
        self.assertEqual(attachment.name, 'VENDOR-0042 - Generated by Odoo.pdf')

    def test_other_pdf_attachment_name_is_unchanged(self):
        attachment = self._attachment('Contract with Odoo partner.pdf')
        self.assertEqual(attachment.name, 'Contract with Odoo partner.pdf')

    def test_same_name_on_another_model_is_unchanged(self):
        attachment = self._attachment(
            'Note - Generated by Odoo.pdf', res_model='res.partner', res_id=self.env.user.partner_id.id)
        self.assertIsNotNone(re.search(r'\bOdoo\b', attachment.name))
