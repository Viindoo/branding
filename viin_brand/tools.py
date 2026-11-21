import io
import logging
import re

from lxml import etree

from odoo.tools import pdf

_logger = logging.getLogger(__name__)

PRODUCT_NAME = 'Viindoo'
# A document larger than this is printed as it is: the rewrite loads the whole document a second
# time in memory only to set two metadata entries, which is not worth the cost on a very large report.
BRAND_PDF_MAX_BYTES = 64 * 1024 * 1024
XMP_NAMESPACES = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'pdf': 'http://ns.adobe.com/pdf/1.3/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xmp': 'http://ns.adobe.com/xap/1.0/',
}


def debrand_exception(error):
    """Replace the product name Odoo with Viindoo in the message of an exception.

    :param error: an exception whose first argument is its message; one without a text message is
        returned unchanged
    :return: the same exception
    """
    message, *rest = error.args or (None,)
    if isinstance(message, str):
        error.args = (re.sub(r'\bOdoo\b', PRODUCT_NAME, message), *rest)
    return error


def brand_xmp(content):
    """Make the XMP packet of a PDF name Viindoo as the tool that produced the document.

    The producer and the creator tool are the XMP counterparts of the ``/Producer`` and
    ``/Creator`` entries of the document information, which a PDF/A document must keep equal, so
    both are set to the value of those entries. The product name in the creator and the
    description is replaced; every other value, the title included, is kept.

    :param bytes content: the XMP packet
    :return: the packet to store, ``content`` itself when it needs no change or is not XML
    :rtype: bytes
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    try:
        tree = etree.parse(io.BytesIO(content), parser)
    except etree.XMLSyntaxError:
        return content
    changed = False
    for node in tree.xpath('//pdf:Producer | //xmp:CreatorTool', namespaces=XMP_NAMESPACES):
        if node.text != PRODUCT_NAME or len(node):
            node[:] = []
            node.text = PRODUCT_NAME
            changed = True
    for node in tree.xpath('//dc:creator//rdf:li | //dc:description//rdf:li', namespaces=XMP_NAMESPACES):
        text = re.sub(r'\bOdoo\b', PRODUCT_NAME, node.text or '')
        if text != (node.text or ''):
            node.text = text
            changed = True
    return etree.tostring(tree, encoding='UTF-8', xml_declaration=False) if changed else content


def brand_pdf(content):
    """Return a PDF document whose creator and producer are Viindoo, the other entries kept.

    The rewrite only sets metadata, so it never prevents a print: content that is
    not a PDF document (no PDF header in its first kilobyte, where a reader looks
    for it) or is larger than ``BRAND_PDF_MAX_BYTES`` is returned as it is, and so
    is a PDF document that cannot be read or fails in the PDF library, with a
    warning.

    :param bytes content: the output of a report renderer
    :return: the rewritten document, ``content`` itself when it is not rewritten
    :rtype: bytes
    """
    is_pdf = bool(content) and b'%PDF-' in content[:1024]
    if not is_pdf or len(content) > BRAND_PDF_MAX_BYTES:
        return content
    try:
        reader = pdf.PdfFileReader(io.BytesIO(content), strict=False)
        writer = pdf.PdfFileWriter()
        writer.cloneReaderDocumentRoot(reader)
        info = reader.getDocumentInfo() or {}
        writer.addMetadata({key: value for key, value in info.items() if key not in ('/Creator', '/Producer')})
        with io.BytesIO() as buffer:
            writer.write(buffer)
            return buffer.getvalue()
    except Exception as error:  # noqa: BLE001 - branding must never break a print
        _logger.warning("The PDF metadata could not be set (%s), the document is kept as it is", type(error).__name__)
        return content
