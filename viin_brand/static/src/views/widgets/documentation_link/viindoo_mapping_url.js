/** @odoo-module **/

/* Odoo CE 19.0 documentation links.
 * Keys: exact paths from Odoo 19.0 XML (documentation= and documentation_link path=).
 * Values: the Viindoo doc URL, or "" when no Viindoo page exists.
 *
 * documentation_link.js applies a value by case:
 *   - non-empty value -> the Viindoo URL is used.
 *   - ""              -> the link is hidden (the template renders it only when `url` is truthy).
 *   - key absent      -> a link to odoo.com is hidden; a link to a third party is kept.
 */

export const ODOO_VIINDOO_DOCUMENTATION_MAPPING = {
    /* account */
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/fiscal-localizations/fiscal-localizations-packages.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/default_taxes.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/taxation/default-taxes.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/taxcloud.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/avatax.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/eu_distance_selling.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/cash_basis_taxes.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/taxation/manage-taxes-in-a-cash-basis-taxpayer.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/others/multi_currency.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/multi-currencies/how-to-configure-a-multi-currencies-system.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_invoices/snailmail.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/different_addresses.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/send-quotations/manage-invoicing-address-and-delivery-address-in-sales.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_invoices/cash_rounding.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-invoices/settings/configure-cash-rounding-method.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/reporting/declarations/intrastat.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_payments/online_payment.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/online-payment-on-website.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_payments/batch.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_payments/batch_sdd.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/receivables/customer_invoices/epc_qr_code.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/how-to-make-a-payment-with-emv-qr-code.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/pay/check.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-payables/vendor-payments/how-to-print-checks-to-pay-vendors.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/pay/sepa.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/pay/trusted_accounts.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-payables/vendor-payments/how-to-trust-a-vendor-bank-account.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/payables/supplier_bills/invoice_digitization.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/others/analytic_accounting.html":
        "https://viindoo.com/documentation/19.0/applications/finance/analytic/analytic-account-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/others/adviser/budget.html":
        "https://viindoo.com/documentation/19.0/applications/finance/analytic/budget-management.html",
    /* auth_oauth */
    "https://www.odoo.com/documentation/19.0/applications/general/auth/google.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/system-settings/sign-in-with-google-authentication.html",
    /* base_setup */
    "https://www.odoo.com/documentation/19.0/applications/general/users.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/manage-users/user-account-setting-and-management.html",
    "https://www.odoo.com/documentation/19.0/applications/marketing/sms_marketing/pricing/pricing_and_faq.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/general/export_import_data.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/guiding-to-import-and-export-data.html",
    "https://www.odoo.com/documentation/19.0/applications/productivity/mail_plugins.html": "",
    "https://www.odoo.com/documentation/19.0/applications/general/auth/ldap.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/external-apps-integration/ldap.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/optimize/unsplash.html":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    "https://www.odoo.com/documentation/19.0/applications/general/integrations/geolocation.html":
        "https://viindoo.com/documentation/19.0/applications/productivity/contact/create-a-new-contact-in-viindoo.html#how-do-i-show-a-contact-on-the-map",
    /* base_vat */
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/vat_validation.html":
        "",
    /* calendar */
    "https://www.odoo.com/documentation/19.0/applications/productivity/calendar/outlook.html":
        "https://viindoo.com/documentation/19.0/applications/productivity/calendar/sychronization-with-outlook-s-calendar.html",
    "https://www.odoo.com/documentation/19.0/applications/productivity/calendar/google.html":
        "https://viindoo.com/documentation/19.0/applications/productivity/calendar/sychronization-with-google-s-calendar.html",
    /* crm */
    "https://www.odoo.com/documentation/19.0/applications/sales/crm/track_leads/lead_scoring.html#assign-leads":
        "https://viindoo.com/documentation/19.0/applications/sales/crm/organize-the-pipeline/lead-scoring-and-automatic-lead-assignment.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/crm/acquire_leads/lead_mining.html":
        "",
    /* digest */
    "https://www.odoo.com/documentation/19.0/applications/general/digest_emails.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/system-settings/how-to-send-kpi-digest-emails.html",
    "https://www.odoo.com/documentation/19.0/applications/general/digest_emails.html#custom-digest-emails":
        "https://viindoo.com/documentation/19.0/developer/development/managing-emails-in-odoo.html",
    /* hr_timesheet */
    "https://www.odoo.com/documentation/19.0/applications/services/timesheets/time_off.html":
        "https://viindoo.com/documentation/19.0/applications/services/timesheets/how-to-create-timesheets-upon-other-apps.html",
    /* iap */
    "https://www.odoo.com/documentation/19.0/applications/general/in_app_purchase.html": "",
    /* mail */
    "https://www.odoo.com/documentation/19.0/applications/general/email_communication/email_servers.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/general/email_communication/email_domain.html#be-spf-compliant":
        "https://viindoo.com/documentation/19.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    /* Core hardcodes the ICE server links as absolute URLs with a literal "latest" segment, so
    the keys carry "latest", not "19.0". */
    "https://www.odoo.com/documentation/latest/applications/productivity/discuss/ice_servers.html":
        "https://viindoo.com/documentation/19.0/applications/productivity/discuss/set-up-calls-with-twilio-and-ice-servers.html",
    "https://www.odoo.com/documentation/latest/applications/productivity/discuss/ice_servers.html#define-a-list-of-custom-ice-servers":
        "https://viindoo.com/documentation/19.0/applications/productivity/discuss/set-up-calls-with-twilio-and-ice-servers.html",
    /* mrp */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/bill_configuration.html#adding-a-routing":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/manufacturing/products/how-to-create-bills-of-materials.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/subcontracting.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/manufacturing/operations/manage-subcontracts-in-your-manufacturing-proccess.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/use_mps.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/manufacturing/planning/how-to-use-the-master-production-schedule-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/productivity/iot/devices/printer.html":
        "",
    /* payment_adyen */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/adyen.html#place-a-hold-on-a-card":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    /* payment_authorize */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/authorize.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    /* point_of_sale */
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/cash_rounding.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/shop-features/steps-to-activate-cash-rounding-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/accounting/taxation/taxes/B2B_B2C.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/taxation/how-to-manage-price-tax-included-n-excluded.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/shop-features/set-up-payment-methods-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/vantiv.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/six.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/adyen.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/stripe.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/viva_com.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/razorpay.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/mercado_pago.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/pine_labs.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals/qfpay.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/configuration/epos_ssc.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/shop-features/print-receipts-on-an-epson-epos-printer.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/employee_login.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/shop-features/steps-for-cashiers-to-log-in-pos-shop.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/discounts.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/how-to-apply-discount.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/loyalty.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/steps-to-setup-loyalty-program.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/pricelists.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/pricing-features/guideline-to-setup-pricelist-in-pos.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/pricing/fiscal_position.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/restaurant-features/using-fiscal-position-in-point-of-sale.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/receipts_invoices.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/shop-features/manage-pos-bill.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/restaurant/tips.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/restaurant-features/applying-bonus-amount-on-payment.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/shop/customer_display.html":
        "https://viindoo.com/documentation/19.0/applications/internet-of-things/iot-integration/iot-integration-for-pos.html",
    /* pos_restaurant */
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/restaurant/floors_tables.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/restaurant-features/restaurant-reservation-management.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/restaurant/bill_printing.html":
        "https://viindoo.com/documentation/19.0/applications/sales/point-of-sale/restaurant-features/steps-to-split-bills-in-pos.html",
    /* product */
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/products/product_images.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/products/auto-upload-product-images-from-google.html",
    /* purchase */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase/manage_deals/agreements.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/purchase/manage-deals/purchase-agreement-blaket-orders.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase/manage_deals/control_bills.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/purchase/manage-deals/vendor-bills-control.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/products/uom.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/products/activate-different-units-of-measure.html",
    /* purchase_stock */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/shipping/operation/dropshipping.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/mto.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/products/all-about-replenishment-rules-make-to-orders-minimum-stock-and-more.html",
    /* sale */
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/products/variants.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/products/using-product-variants-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/prices/pricing.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/manage-your-pricing/manage-multiple-prices-per-product.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/get_signature_to_validate.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/send-quotations/activate-e-sign-feature-to-confirm-order.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/get_paid_to_validate.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/send-quotations/activate-online-payment-for-viindoo-website.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/shipping/setup/third_party_shipper.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/shipping/configure-delivery-methods.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/invoicing/invoicing_policy.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/invoicing-method/issuing-invoices-based-on-order-quantity-or-delivery-quantity.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/invoicing/down_payment.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/invoicing-method/down-payment-in-viindoo-sales.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/amazon_connector/setup.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/gelato.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/advanced-topics/sell-print-on-demand-products-with-gelato.html",
    /* sale_management */
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/quote_template.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/send-quotations/designing-quotation-template-for-fast-and-efficient-sales-process.html",
    /* sale_pdf_quote_builder */
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/send_quotations/pdf_quote_builder.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/send-quotations/designing-quotation-template-for-fast-and-efficient-sales-process.html",
    /* sale_stock */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/planning/scheduled_dates.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/planning/understanding-the-scheduled-delivery-date-computation.html",
    /* stock */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/product_management/product_tracking/package.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/products/how-to-use-different-units-of-measure-packages-or-packaging.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/products/usage.html#packages":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/products/how-to-use-different-units-of-measure-packages-or-packaging.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/misc/batch_transfers.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/miscellaneous-operations/how-to-use-batch-transfers.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing/management/quality_control.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/quality-management/getting-started-with-viindoo-quality.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/barcode/setup/software.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/barcode/barcode-scanner-integration.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/products/usage.html#packaging":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/products/how-to-use-different-units-of-measure-packages-or-packaging.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/lots-serial-numbers/difference-between-lots-and-serial-numbers.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/lots-serial-numbers/product-expiration-dates.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/misc/owned_stock.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/miscellaneous-operations/how-to-manage-consignment-products.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/warehouses/warehouses_locations.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/warehouses/difference-between-warehouses-and-locations.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/routes/concepts/use_routes.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/advanced-routes/understanding-pull-push-rules-in-supply-routes.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/delivery/dropshipping.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/use_locations.html":
        "https://viindoo.com/documentation/19.0/applications/supply-chain/inventory/warehouse-management/warehouses/how-to-create-warehouses-and-locations.html",
    /* stock_account */
    "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/management/reporting/integrating_landed_costs.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/inventory/accounting-for-landed-cost.html",
    /* web_unsplash */
    "https://www.odoo.com/documentation/19.0/applications/websites/website/optimize/unsplash.html#generate-an-unsplash-access-key":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    /* website */
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/domain_names.html#domain-name-website-map":
        "https://viindoo.com/documentation/19.0/applications/websites/website/publish/how-to-use-your-own-domain-name.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/translate.html":
        "https://viindoo.com/documentation/19.0/applications/websites/website/publish/how-to-setup-a-multi-language-website.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/reporting/analytics.html#analytics-plausible":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-with-plausible.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/reporting/analytics.html#analytics-google-analytics":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-in-google-analytics.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/cdn.html":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-serve-your-website-through-a-cdn.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/google_search_console.html":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-monitor-your-website-with-google-search-console.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/cookies_bar.html":
        "https://viindoo.com/documentation/19.0/applications/websites/website/publish/how-to-display-a-cookies-bar-on-your-website.html",
    /* website_payment */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    /* website_sale */
    "https://www.odoo.com/documentation/19.0/applications/websites/website/configuration/address_autocomplete.html":
        "https://viindoo.com/documentation/19.0/applications/sales/ecommerce/getting-started/validate-customer-addresses-with-google-places.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/managing_products/variants.html":
        "https://viindoo.com/documentation/19.0/applications/getting-started/products/using-product-variants-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/loyalty_discount.html":
        "https://viindoo.com/documentation/19.0/applications/sales/sales/gift/set-up-discount-and-loyalty-programs.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/ecommerce_management/order_handling.html#abandoned-cart":
        "https://viindoo.com/documentation/19.0/applications/sales/ecommerce/maximize-your-revenue/follow-up-abandoned-carts.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/google_merchant_center.html":
        "https://viindoo.com/documentation/19.0/applications/sales/ecommerce/maximize-your-revenue/publish-products-to-google-merchant-center.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/ecommerce/shipping.html#click-collect":
        "https://viindoo.com/documentation/19.0/applications/sales/ecommerce/maximize-your-revenue/let-customers-pick-up-orders-in-store.html",

    /* payment providers, localizations, mail servers, kiosk and website reporting */
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/paypal.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/how-to-make-a-payment-with-paypal.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/payment_providers/razorpay.html#payment-providers-razorpay-recurring-payments":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/singapore.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/hong_kong.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/brazil.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html#india-e-invoicing":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html#india-e-waybill":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html#india-gstr":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html#indian-check-gstin-status":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/spain.html#veri-factu":
        "",
    "https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/vietnam.html":
        "https://viindoo.com/documentation/19.0/applications/finance/accounting-and-invoicing/fiscal-localizations/issue-e-invoice-by-integrating-viindoo-with-viettel-s-s-invoice-service.html",
    "https://www.odoo.com/documentation/19.0/applications/general/email_communication/email_servers.html?highlight=outgoing email server#use-a-default-from-email-address":
        "https://viindoo.com/documentation/19.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "https://www.odoo.com/documentation/19.0/administration/on_premise/geo_ip.html":
        "https://viindoo.com/documentation/19.0/developer/development/cms-website-development.html",
    "https://www.odoo.com/documentation/19.0/_downloads/eaa2883bd361273b475c9765f64e3e0c/pdfquotebuilderexamples.zip":
        "",
    "https://www.odoo.com/documentation/19.0/applications/hr/attendances/hardware.html":
        "https://viindoo.com/documentation/19.0/applications/human-resources/attendances/operations/set-up-the-attendance-kiosk.html",
    "https://www.odoo.com/documentation/19.0/applications/websites/website/reporting/plausible.html":
        "https://viindoo.com/documentation/19.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-with-plausible.html",
    "https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html":
        "https://viindoo.com/documentation/19.0/developer/started/odoo-orm-basic.html",
};
