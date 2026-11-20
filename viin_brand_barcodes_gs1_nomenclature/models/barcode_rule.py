from odoo import fields, models


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    gs1_content_type = fields.Selection(
        help="The GS1 content type defines what kind of data the rule will process the barcode as:\
        * Date: the barcode will be converted into a datetime;\
        * Measure: the barcode's value is related to a specific unit;\
        * Numeric Identifier: fixed length barcode following a specific encoding;\
        * Alpha-Numeric Name: variable length barcode.")
