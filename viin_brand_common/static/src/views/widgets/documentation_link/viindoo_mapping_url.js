/** @odoo-module **/

/* Define documentation of odoo which will be replaced by Viindoo one on setting pages only,
if none found the system will fallback to the original one of odoo
This approach help we manage nearly all odoo documentation to be replaced or not
 */

export const ODOO_VIINDOO_DOCUMENTATION_MAPPING = {
    /* account */
    "https://www.odoo.com/documentation/17.0/applications/finance/fiscal_localizations.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxation/taxes/default_taxes.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxation/taxes/taxcloud.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxation/taxes/avatax.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxation/taxes/eu_distance_selling.html": "https://viindoo.com/documentation/16.0/applications/finance/accounting-and-invoicing/taxation/distance-selling-for-eu-intra-community.html",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxation/taxes/cash_basis_taxes.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/others/multi_currency.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/receivables/customer_invoices/snailmail.html": "",
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/send_quotations/different_addresses.html": "https://viindoo.com/documentation/16.0/applications/sales/sales/send-quotations/manage-invoicing-address-and-delivery-address-in-sales.html",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/receivables/customer_invoices/cash_rounding.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/reporting/declarations/intrastat.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/receivables/customer_payments/online_payment.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/receivables/customer_payments/batch.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/receivables/customer_payments/batch_sdd.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/receivables/customer_invoices/epc_qr_code.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/payables/pay/check.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/payables/pay/sepa.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/payables/supplier_bills/invoice_digitization.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/others/analytic_accounting.html": "",
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/others/adviser/budget.html": "",
    /* auth_oauth */
    "https://www.odoo.com/documentation/17.0/applications/general/auth/google.html": "https://viindoo.com/documentation/16.0/applications/getting-started/system-settings/sign-in-with-google-authentication.html",
    /* base_setup */
    "https://www.odoo.com/documentation/17.0/applications/marketing/sms_marketing/pricing/pricing_and_faq.html": "",
    "https://www.odoo.com/documentation/17.0/applications/general/export_import_data.html": "https://viindoo.com/documentation/16.0/applications/getting-started/guiding-to-import-and-export-data.html#import-data-into-viindoo-software",
    "https://www.odoo.com/documentation/17.0/applications/productivity/mail_plugins.html": "https://viindoo.com/documentation/16.0/applications/getting-started.html",
    "https://www.odoo.com/documentation/17.0/applications/general/auth/ldap.html": "https://viindoo.com/documentation/16.0/applications/getting-started/external-apps-integration/ldap.html?highlight=ldap",
    "https://www.odoo.com/documentation/17.0/applications/websites/website/optimize/unsplash.html": "https://viindoo.com/documentation/16.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    /* base_vat */
    "https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxation/taxes/vat_validation.html": "",
    /* calendar */
    "https://www.odoo.com/documentation/17.0/applications/productivity/calendar/outlook.html": "https://viindoo.com/documentation/16.0/applications/productivity/calendar/sychronization-with-outlook-s-calendar.html",
    "https://www.odoo.com/documentation/17.0/applications/productivity/calendar/google.html": "https://viindoo.com/documentation/16.0/applications/productivity/calendar/sychronization-with-google-s-calendar.html",
    /* crm */
    "https://www.odoo.com/documentation/17.0/applications/sales/crm/track_leads/lead_scoring.html#assign-leads": "",
    "https://www.odoo.com/documentation/17.0/applications/sales/crm/acquire_leads/lead_mining.html": "",
    /* digest */
    "https://www.odoo.com/documentation/17.0/applications/general/digest_emails.html": "",
    /* event */
    /* hr_recruitment */
    /* hr_timesheet */
    "https://www.odoo.com/documentation/17.0/applications/services/timesheets/overview/time_off.html": "",
    /* iap */
    "https://www.odoo.com/documentation/17.0/applications/general/in_app_purchase.html": "",
    /* mail */
    "https://www.odoo.com/documentation/17.0/applications/general/email_communication/email_servers.html": "https://viindoo.com/documentation/16.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "https://www.odoo.com/documentation/17.0/applications/general/email_communication/email_domain.html#be-spf-compliant": "",
    /* mrp */
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/manufacturing/management/bill_configuration.html#adding-a-routing": "https://viindoo.com/documentation/16.0/applications/supply-chain/manufacturing/products/how-to-create-bills-of-materials.html",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/manufacturing/management/subcontracting.html": "https://viindoo.com/documentation/16.0/applications/supply-chain/manufacturing/operations/manage-subcontracts-in-your-manufacturing-proccess.html",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/manufacturing/management/use_mps.html": "https://viindoo.com/documentation/16.0/applications/supply-chain/manufacturing/planning/how-to-use-the-master-production-schedule-in-viindoo.html",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/planning/scheduled_dates.html": "https://viindoo.com/documentation/16.0/applications/supply-chain/inventory/warehouse-management/planning/understanding-the-scheduled-delivery-date-computation.html",
    /* point_of_sale */
    "https://www.odoo.com/documentation/17.0/applications/sales/point_of_sale/pricing/cash_rounding.html": "https://viindoo.com/documentation/16.0/applications/finance/accounting-and-invoicing/account-receivables/customer-invoices/settings/configure-cash-rounding-method.html",
    "https://www.odoo.com/documentation/17.0/applications/sales/point_of_sale/payment_methods/terminals/vantiv.html": "https://viindoo.com/documentation/16.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/17.0/applications/sales/point_of_sale/payment_methods/terminals/six.html": "https://viindoo.com/documentation/16.0/applications/sales/point-of-sale/pricing-features/payment-with-six-payment-terminal-in-pos.html",
    /* product */
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/products_prices/products/product_images.html": "",
    /* purchase */
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/purchase/manage_deals/agreements.html": "https://viindoo.com/documentation/16.0/applications/supply-chain/purchase/manage-deals/purchase-agreement-blaket-orders.html",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/purchase/manage_deals/control_bills.html": "https://viindoo.com/documentation/16.0/applications/supply-chain/purchase/manage-deals/vendor-bills-control.html",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/products/uom.html": "",
    /* purchase_stock */
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/shipping/operation/dropshipping.html": "https://viindoo.com/documentation/16.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    /* sale */
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/products_prices/products/variants.html": "https://viindoo.com/documentation/16.0/applications/getting-started/products/using-product-variants-in-viindoo.html",
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/products_prices/prices/pricing.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/shipping/setup/third_party_shipper.html": "",
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/invoicing/invoicing_policy.html": "",
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/invoicing/down_payment.html": "",
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/amazon_connector/setup.html": "",
    /* sale_management */
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/send_quotations/quote_template.html": "",
    /* sale_pdf_quote_builder */
    "https://www.odoo.com/documentation/17.0/applications/sales/sales/send_quotations/pdf_quote_builder.html": "",
    /* sale_stock */
    /* stock */
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/products/usage.html#packages": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/misc/batch_transfers.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/manufacturing/management/quality_control.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/barcode/setup/software.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/products/usage.html#packaging": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/misc/owned_stock.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/warehouses/warehouses_locations.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/routes/concepts/use_routes.html": "",
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/delivery/dropshipping.html": "",
    /* stock_account */
    "https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/management/reporting/integrating_landed_costs.html": "",
    /* web_unsplash */
    "https://www.odoo.com/documentation/17.0/applications/websites/website/optimize/unsplash.html#generate-an-unsplash-access-key": "",
    /* website */
    "https://www.odoo.com/documentation/17.0/applications/websites/website/configuration/cookies_bar.html": "",
    /* website_sale */
};
