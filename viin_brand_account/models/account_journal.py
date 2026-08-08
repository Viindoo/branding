from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    inbound_payment_method_line_ids = fields.One2many(
        help="Manual: Get paid by any method outside of the system.\n"
        "Payment Providers: Each payment provider has its own Payment Method. Request a transaction on/to a card thanks to a payment token saved by the partner when buying or subscribing online.\n"
        "Batch Deposit: Collect several customer checks at once generating and submitting a batch deposit to your bank. Module account_batch_payment is necessary.\n"
        "SEPA Direct Debit: Get paid in the SEPA zone thanks to a mandate your partner will have granted to you. Module account_sepa is necessary.\n")

    outbound_payment_method_line_ids = fields.One2many(
        help="Manual: Pay by any method outside of the system.\n"
        "Check: Pay bills by check and print it from the system.\n"
        "SEPA Credit Transfer: Pay in the SEPA zone by submitting a SEPA Credit Transfer file to your bank. Module account_sepa is necessary.\n"
    )

    alias_id = fields.Many2one(help="Send one separate email for each invoice.\n\n"
                               "Any file extension will be accepted.\n\n"
                               "Only PDF and XML files will be interpreted by the system")

    invoice_reference_model = fields.Selection(
        help="You can choose different models for each type of reference. "
        "The default one is the system reference.")
