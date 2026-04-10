/** @odoo-module **/

/* Full inventory of Odoo CE 19.0 documentation links.
 * Keys: exact paths from Odoo 19.0 XML (documentation= and documentation_link path=).
 * Values: Viindoo doc URL if available, empty string "" if not yet available.
 *
 * Logic in documentation_link.js:
 *   - Value is non-empty string → use Viindoo URL
 *   - Value is "" or key not found → fallback to original Odoo link
 *
 * To contribute: find the empty "" entry, write the Viindoo doc page, fill in the URL.
 */

export const ODOO_VIINDOO_DOCUMENTATION_MAPPING = {
    /* account */
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/fiscal-localizations/fiscal-localizations-packages.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/default_taxes.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/taxation/taxes-and-tax-rule-configuration.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/eu_distance_selling.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/cash_basis_taxes.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/others/multi_currency.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/multi-currencies/how-to-configure-a-multi-currencies-system.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_invoices/snailmail.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/different_addresses.html":
        "https://viindoo.com/documentation/17.0/applications/sales/sales/send-quotations/manage-invoicing-address-and-delivery-address-in-sales.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_invoices/cash_rounding.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/account-receivables/customer-invoices/settings/configure-cash-rounding-method.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/reporting/declarations/intrastat.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_payments/online_payment.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/online-payment-on-website.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_payments/batch.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_payments/batch_sdd.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_invoices/epc_qr_code.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/pay/check.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/pay/sepa.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/pay/trusted_accounts.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/supplier_bills/invoice_digitization.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/others/analytic_accounting.html":
        "https://viindoo.com/documentation/17.0/applications/finance/analytic/analytic-account-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/others/adviser/budget.html":
        "https://viindoo.com/documentation/17.0/applications/finance/analytic/budget-management.html",
    /* auth_oauth */
    "https://www.odoo.com/documentation/19.0/applications/general/auth/google.html":
        "https://viindoo.com/documentation/16.0/applications/getting-started/system-settings/sign-in-with-google-authentication.html",
    /* base_setup */
    "https://www.odoo.com/documentation/19.0/applications/general/users.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/marketing/sms_marketing/pricing/pricing_and_faq.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/general/export_import_data.html":
        "https://viindoo.com/documentation/17.0/applications/getting-started/guiding-to-import-and-export-data.html",
    "https://www.odoo.com/documentation/19.0/applications/productivity/mail_plugins.html":
        "https://viindoo.com/documentation/17.0/developer/development/managing-emails-in-odoo.html",
    "https://www.odoo.com/documentation/19.0/applications/general/auth/ldap.html":
        "https://viindoo.com/documentation/15.0/applications/getting-started/external-apps-integration/ldap.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/optimize/unsplash.html":
        "https://viindoo.com/documentation/17.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    "https://www.odoo.com/documentation/19.0/applications/general/integrations/geolocation.html":
        "",
    /* base_vat */
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/vat_validation.html":
        "",
    /* calendar */
    "https://www.odoo.com/documentation/19.0/applications/productivity/calendar/outlook.html":
        "https://viindoo.com/documentation/17.0/applications/productivity/calendar/sychronization-with-outlook-s-calendar.html",
    "https://www.odoo.com/documentation/19.0/applications/productivity/calendar/google.html":
        "https://viindoo.com/documentation/17.0/applications/productivity/calendar/sychronization-with-google-s-calendar.html",
    /* crm */
    "https://www.odoo.com/documentation/19.0/applications/sales/crm/track_leads/lead_scoring.html#assign-leads":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/crm/acquire_leads/lead_mining.html":
        "",
    /* digest */
    "https://www.odoo.com/documentation/19.0/applications/general/digest_emails.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/general/digest_emails.html#custom-digest-emails":
        "",
    /* hr_timesheet */
    "https://www.odoo.com/documentation/19.0/applications/services/timesheets/time_off.html":
        "https://viindoo.com/documentation/17.0/applications/human-resources/time-off/how-to-create-time-off-types.html",
    /* iap */
    "https://www.odoo.com/documentation/19.0/applications/general/in_app_purchase.html":
        "",
    /* mail */
    "https://www.odoo.com/documentation/19.0/applications/general/email_communication/email_servers.html":
        "https://viindoo.com/documentation/17.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/general/email_communication/email_domain.html#be-spf-compliant":
        "https://viindoo.com/documentation/17.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-retiring-emails-in-viindoo.html",
    /* mrp */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/bill_configuration.html#adding-a-routing":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/manufacturing/products/how-to-create-bills-of-materials.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/subcontracting.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/manufacturing/operations/manage-subcontracts-in-your-manufacturing-proccess.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/use_mps.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/manufacturing/planning/how-to-use-the-master-production-schedule-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/productivity/iot/devices/printer.html":
        "",
    /* payment_adyen */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/adyen.html#place-a-hold-on-a-card":
        "",
    /* payment_authorize */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/authorize.html":
        "",
    /* point_of_sale */
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/cash_rounding.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/account-receivables/customer-invoices/settings/configure-cash-rounding-method.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/B2B_B2C.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/adyen.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/stripe.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/viva_com.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/razorpay.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/mercado_pago.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/pine_labs.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/qfpay.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/configuration/epos_ssc.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/employee_login.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/discounts.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/loyalty.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/pricelists.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/fiscal_position.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/receipts_invoices.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/restaurant/tips.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/shop/customer_display.html":
        "",
    /* pos_restaurant */
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/restaurant/floors_tables.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/restaurant/bill_printing.html":
        "",
    /* purchase */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase/manage_deals/agreements.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/purchase/manage-deals/purchase-agreement-blaket-orders.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase/manage_deals/control_bills.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/purchase/manage-deals/vendor-bills-control.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/products/uom.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/products/activate-different-units-of-measure.html",
    /* purchase_stock */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/shipping/operation/dropshipping.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/mto.html":
        "",
    /* sale */
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/products/variants.html":
        "https://viindoo.com/documentation/17.0/applications/getting-started/products/using-product-variants-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/prices/pricing.html":
        "https://viindoo.com/documentation/17.0/applications/sales/sales/manage-your-pricing/manage-multiple-prices-per-product.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/get_signature_to_validate.html":
        "https://viindoo.com/documentation/16.0/applications/sales/sales/send-quotations/activate-e-sign-feature-to-confirm-order.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/get_paid_to_validate.html":
        "https://viindoo.com/documentation/16.0/applications/sales/sales/send-quotations/activate-online-payment-for-viindoo-website.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/shipping/setup/third_party_shipper.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/shipping/configure-delivery-methods.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/invoicing/invoicing_policy.html":
        "https://viindoo.com/documentation/17.0/applications/sales/sales/invoicing-method/invoice-based-on-timing-of-service-provision.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/amazon_connector/setup.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/gelato.html":
        "",
    /* sale_management */
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/quote_template.html":
        "https://viindoo.com/documentation/17.0/applications/sales/sales/send-quotations/designing-quotation-template-for-fast-and-efficient-sales-process.html",
    /* sale_stock */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/planning/scheduled_dates.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/planning/understanding-the-scheduled-delivery-date-computation.html",
    /* stock */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/product_management/product_tracking/package.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/misc/batch_transfers.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/miscellaneous-operations/how-to-use-batch-transfers.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/quality_control.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/quality-management/getting-started-with-viindoo-quality.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/barcode/setup/software.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/barcode/barcode-scanner-integration.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/lots-serial-numbers/difference-between-lots-and-serial-numbers.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/lots-serial-numbers/product-expiration-dates.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/misc/owned_stock.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/miscellaneous-operations/how-to-manage-consignment-products.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/routes/concepts/use_routes.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/advanced-routes/understanding-pull-push-rules-in-supply-routes.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/delivery/dropshipping.html":
        "https://viindoo.com/documentation/17.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/use_locations.html":
        "",
    /* stock_account */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/reporting/integrating_landed_costs.html":
        "https://viindoo.com/documentation/17.0/applications/finance/accounting-and-invoicing/inventory/accounting-for-landed-cost.html",
    /* web_unsplash */
    "https://www.odoo.com/documentation/19.0/applications/websites/website/optimize/unsplash.html#generate-an-unsplash-access-key":
        "https://viindoo.com/documentation/17.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    /* website */
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/domain_names.html#domain-name-website-map":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/translate.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/reporting/analytics.html#analytics-plausible":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/reporting/analytics.html#analytics-google-analytics":
        "https://viindoo.com/documentation/16.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-in-google-analytics.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/cdn.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/google_search_console.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/cookies_bar.html":
        "",
    /* website_payment */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers.html":
        "",
    /* website_sale */
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/address_autocomplete.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/managing_products/variants.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/loyalty_discount.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/ecommerce_management/order_handling.html#abandoned-cart":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/google_merchant_center.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/shipping.html#click-collect":
        "",
};
