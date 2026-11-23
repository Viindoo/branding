/* Odoo documentation links.
 * Keys: the path of a documentation page after its series segment (`/documentation/<series>`),
 * as written in the XML of the views (`documentation=` and `documentation_link path=`), anchor and
 * query string included, so that a final build and a development build of any series find the same
 * entry.
 * Values: the Viindoo doc URL, or "" when no Viindoo page exists.
 *
 * documentation_link.js applies a value by case:
 *   - non-empty value -> the Viindoo URL is used.
 *   - ""              -> the link is hidden (the template renders it only when `url` is truthy).
 *   - key absent      -> a link to odoo.com is hidden; a link to a third party is kept.
 */

export const ODOO_VIINDOO_DOCUMENTATION_MAPPING = {
    /* account */
    "/applications/finance/fiscal_localizations.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/fiscal-localizations/fiscal-localizations-packages.html",
    "/applications/finance/accounting/taxation/taxes/default_taxes.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/taxation/default-taxes.html",
    "/applications/finance/accounting/taxation/taxes/taxcloud.html": "",
    "/applications/finance/accounting/taxation/taxes/avatax.html": "",
    "/applications/finance/accounting/taxation/taxes/eu_distance_selling.html": "",
    "/applications/finance/accounting/taxation/taxes/cash_basis_taxes.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/taxation/manage-taxes-in-a-cash-basis-taxpayer.html",
    "/applications/finance/accounting/others/multi_currency.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/multi-currencies/how-to-configure-a-multi-currencies-system.html",
    "/applications/finance/accounting/receivables/customer_invoices/snailmail.html": "",
    "/applications/sales/sales/send_quotations/different_addresses.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/send-quotations/manage-invoicing-address-and-delivery-address-in-sales.html",
    "/applications/finance/accounting/receivables/customer_invoices/cash_rounding.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-invoices/settings/configure-cash-rounding-method.html",
    "/applications/finance/accounting/reporting/declarations/intrastat.html": "",
    "/applications/finance/accounting/receivables/customer_payments/online_payment.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/online-payment-on-website.html",
    "/applications/finance/accounting/receivables/customer_payments/batch.html": "",
    "/applications/finance/accounting/receivables/customer_payments/batch_sdd.html": "",
    "/applications/finance/accounting/receivables/customer_invoices/epc_qr_code.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/how-to-make-a-payment-with-emv-qr-code.html",
    "/applications/finance/accounting/payables/pay/check.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-payables/vendor-payments/how-to-print-checks-to-pay-vendors.html",
    "/applications/finance/accounting/payables/pay/sepa.html": "",
    "/applications/finance/accounting/payables/pay/trusted_accounts.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-payables/vendor-payments/how-to-trust-a-vendor-bank-account.html",
    "/applications/finance/accounting/payables/supplier_bills/invoice_digitization.html": "",
    "/applications/finance/accounting/others/analytic_accounting.html":
        "https://viindoo.com/documentation/20.0/applications/finance/analytic/analytic-account-in-viindoo.html",
    "/applications/finance/accounting/others/adviser/budget.html":
        "https://viindoo.com/documentation/20.0/applications/finance/analytic/budget-management.html",
    /* auth_oauth */
    "/applications/general/auth/google.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/system-settings/sign-in-with-google-authentication.html",
    /* base_setup */
    "/applications/general/users.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/manage-users/user-account-setting-and-management.html",
    "/applications/marketing/sms_marketing/pricing/pricing_and_faq.html": "",
    "/applications/general/export_import_data.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/guiding-to-import-and-export-data.html",
    "/applications/productivity/mail_plugins.html": "",
    "/applications/general/auth/ldap.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/external-apps-integration/ldap.html",
    "/applications/websites/website/optimize/unsplash.html":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    "/applications/general/integrations/geolocation.html":
        "https://viindoo.com/documentation/20.0/applications/productivity/contact/create-a-new-contact-in-viindoo.html#how-do-i-show-a-contact-on-the-map",
    /* base_vat */
    "/applications/finance/accounting/taxation/taxes/vat_validation.html": "",
    /* calendar */
    "/applications/productivity/calendar/outlook.html":
        "https://viindoo.com/documentation/20.0/applications/productivity/calendar/sychronization-with-outlook-s-calendar.html",
    "/applications/productivity/calendar/google.html":
        "https://viindoo.com/documentation/20.0/applications/productivity/calendar/sychronization-with-google-s-calendar.html",
    /* crm */
    "/applications/sales/crm/track_leads/lead_scoring.html#assign-leads":
        "https://viindoo.com/documentation/20.0/applications/sales/crm/organize-the-pipeline/lead-scoring-and-automatic-lead-assignment.html",
    "/applications/sales/crm/acquire_leads/lead_mining.html": "",
    /* digest */
    "/applications/general/digest_emails.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/system-settings/how-to-send-kpi-digest-emails.html",
    "/applications/general/digest_emails.html#custom-digest-emails":
        "https://viindoo.com/documentation/20.0/developer/development/managing-emails-in-odoo.html",
    /* hr_timesheet */
    "/applications/services/timesheets/time_off.html":
        "https://viindoo.com/documentation/20.0/applications/services/timesheets/how-to-create-timesheets-upon-other-apps.html",
    /* iap */
    "/applications/general/in_app_purchase.html": "",
    /* mail */
    "/applications/general/email_communication/email_servers.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "/applications/general/email_communication/email_domain.html#be-spf-compliant":
        "https://viindoo.com/documentation/20.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "/applications/productivity/discuss/ice_servers.html":
        "https://viindoo.com/documentation/20.0/applications/productivity/discuss/set-up-calls-with-twilio-and-ice-servers.html",
    "/applications/productivity/discuss/ice_servers.html#define-a-list-of-custom-ice-servers":
        "https://viindoo.com/documentation/20.0/applications/productivity/discuss/set-up-calls-with-twilio-and-ice-servers.html",
    /* mrp */
    "/applications/inventory_and_mrp/manufacturing/management/bill_configuration.html#adding-a-routing":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/manufacturing/products/how-to-create-bills-of-materials.html",
    "/applications/inventory_and_mrp/manufacturing/management/subcontracting.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/manufacturing/operations/manage-subcontracts-in-your-manufacturing-proccess.html",
    "/applications/inventory_and_mrp/manufacturing/management/use_mps.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/manufacturing/planning/how-to-use-the-master-production-schedule-in-viindoo.html",
    "/applications/productivity/iot/devices/printer.html": "",
    /* payment_adyen */
    "/applications/finance/payment_providers/adyen.html#place-a-hold-on-a-card":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    /* payment_authorize */
    "/applications/finance/payment_providers/authorize.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    /* point_of_sale */
    "/applications/sales/point_of_sale/pricing/cash_rounding.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/shop-features/steps-to-activate-cash-rounding-in-pos.html",
    "/applications/finance/accounting/taxation/taxes/B2B_B2C.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/taxation/how-to-manage-price-tax-included-n-excluded.html",
    "/applications/sales/point_of_sale/payment_methods.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/shop-features/set-up-payment-methods-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/vantiv.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/six.html": "",
    "/applications/sales/point_of_sale/payment_methods/terminals/adyen.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/stripe.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/viva_com.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/razorpay.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/mercado_pago.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/pine_labs.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/payment_methods/terminals/qfpay.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html",
    "/applications/sales/point_of_sale/configuration/epos_ssc.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/shop-features/print-receipts-on-an-epson-epos-printer.html",
    "/applications/sales/point_of_sale/employee_login.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/shop-features/steps-for-cashiers-to-log-in-pos-shop.html",
    "/applications/sales/point_of_sale/pricing/discounts.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/how-to-apply-discount.html",
    "/applications/sales/point_of_sale/pricing/loyalty.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/steps-to-setup-loyalty-program.html",
    "/applications/sales/point_of_sale/pricing/pricelists.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/pricing-features/guideline-to-setup-pricelist-in-pos.html",
    "/applications/sales/point_of_sale/pricing/fiscal_position.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/restaurant-features/using-fiscal-position-in-point-of-sale.html",
    "/applications/sales/point_of_sale/receipts_invoices.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/shop-features/manage-pos-bill.html",
    "/applications/sales/point_of_sale/restaurant/tips.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/restaurant-features/applying-bonus-amount-on-payment.html",
    "/applications/sales/point_of_sale/shop/customer_display.html":
        "https://viindoo.com/documentation/20.0/applications/internet-of-things/iot-integration/iot-integration-for-pos.html",
    /* pos_restaurant */
    "/applications/sales/point_of_sale/restaurant/floors_tables.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/restaurant-features/restaurant-reservation-management.html",
    "/applications/sales/point_of_sale/restaurant/bill_printing.html":
        "https://viindoo.com/documentation/20.0/applications/sales/point-of-sale/restaurant-features/steps-to-split-bills-in-pos.html",
    /* product */
    "/applications/sales/sales/products_prices/products/product_images.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/products/auto-upload-product-images-from-google.html",
    /* purchase */
    "/applications/inventory_and_mrp/purchase/manage_deals/agreements.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/purchase/manage-deals/purchase-agreement-blaket-orders.html",
    "/applications/inventory_and_mrp/purchase/manage_deals/control_bills.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/purchase/manage-deals/vendor-bills-control.html",
    "/applications/inventory_and_mrp/inventory/management/products/uom.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/products/activate-different-units-of-measure.html",
    /* purchase_stock */
    "/applications/inventory_and_mrp/inventory/shipping/operation/dropshipping.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    "/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/mto.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/products/all-about-replenishment-rules-make-to-orders-minimum-stock-and-more.html",
    /* sale */
    "/applications/sales/sales/products_prices/products/variants.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/products/using-product-variants-in-viindoo.html",
    "/applications/sales/sales/products_prices/prices/pricing.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/manage-your-pricing/manage-multiple-prices-per-product.html",
    "/applications/sales/sales/send_quotations/get_signature_to_validate.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/send-quotations/activate-e-sign-feature-to-confirm-order.html",
    "/applications/sales/sales/send_quotations/get_paid_to_validate.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/send-quotations/activate-online-payment-for-viindoo-website.html",
    "/applications/inventory_and_mrp/inventory/shipping/setup/third_party_shipper.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/shipping/configure-delivery-methods.html",
    "/applications/sales/sales/invoicing/invoicing_policy.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/invoicing-method/issuing-invoices-based-on-order-quantity-or-delivery-quantity.html",
    "/applications/sales/sales/invoicing/down_payment.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/invoicing-method/down-payment-in-viindoo-sales.html",
    "/applications/sales/sales/amazon_connector/setup.html": "",
    "/applications/sales/sales/gelato.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/advanced-topics/sell-print-on-demand-products-with-gelato.html",
    /* sale_management */
    "/applications/sales/sales/send_quotations/quote_template.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/send-quotations/designing-quotation-template-for-fast-and-efficient-sales-process.html",
    /* sale_pdf_quote_builder */
    "/applications/sales/sales/send_quotations/pdf_quote_builder.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/send-quotations/designing-quotation-template-for-fast-and-efficient-sales-process.html",
    /* sale_stock */
    "/applications/inventory_and_mrp/inventory/management/planning/scheduled_dates.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/planning/understanding-the-scheduled-delivery-date-computation.html",
    /* stock */
    "/applications/inventory_and_mrp/inventory/product_management/product_tracking/package.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/products/how-to-use-different-units-of-measure-packages-or-packaging.html",
    "/applications/inventory_and_mrp/inventory/management/products/usage.html#packages":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/products/how-to-use-different-units-of-measure-packages-or-packaging.html",
    "/applications/inventory_and_mrp/inventory/management/misc/batch_transfers.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/miscellaneous-operations/how-to-use-batch-transfers.html",
    "/applications/inventory_and_mrp/manufacturing/management/quality_control.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/quality-management/getting-started-with-viindoo-quality.html",
    "/applications/inventory_and_mrp/inventory/barcode/setup/software.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/barcode/barcode-scanner-integration.html",
    "/applications/inventory_and_mrp/inventory/management/products/usage.html#packaging":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/products/how-to-use-different-units-of-measure-packages-or-packaging.html",
    "/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/lots-serial-numbers/difference-between-lots-and-serial-numbers.html",
    "/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/lots-serial-numbers/product-expiration-dates.html",
    "/applications/inventory_and_mrp/inventory/management/misc/owned_stock.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/miscellaneous-operations/how-to-manage-consignment-products.html",
    "/applications/inventory_and_mrp/inventory/management/warehouses/warehouses_locations.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/warehouses/difference-between-warehouses-and-locations.html",
    "/applications/inventory_and_mrp/inventory/routes/concepts/use_routes.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/advanced-routes/understanding-pull-push-rules-in-supply-routes.html",
    "/applications/inventory_and_mrp/inventory/management/delivery/dropshipping.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/delivery-orders/delivery-directly-from-suppliers-to-customers-drop-ship.html",
    "/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/use_locations.html":
        "https://viindoo.com/documentation/20.0/applications/supply-chain/inventory/warehouse-management/warehouses/how-to-create-warehouses-and-locations.html",
    /* stock_account */
    "/applications/inventory_and_mrp/inventory/management/reporting/integrating_landed_costs.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/inventory/accounting-for-landed-cost.html",
    /* web_unsplash */
    "/applications/websites/website/optimize/unsplash.html#generate-an-unsplash-access-key":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html",
    /* website */
    "/applications/websites/website/configuration/domain_names.html#domain-name-website-map":
        "https://viindoo.com/documentation/20.0/applications/websites/website/publish/how-to-use-your-own-domain-name.html",
    "/applications/websites/website/configuration/translate.html":
        "https://viindoo.com/documentation/20.0/applications/websites/website/publish/how-to-setup-a-multi-language-website.html",
    "/applications/websites/website/reporting/analytics.html#analytics-plausible":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-with-plausible.html",
    "/applications/websites/website/reporting/analytics.html#analytics-google-analytics":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-in-google-analytics.html",
    "/applications/websites/website/configuration/cdn.html":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-serve-your-website-through-a-cdn.html",
    "/applications/websites/website/configuration/google_search_console.html":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-monitor-your-website-with-google-search-console.html",
    "/applications/websites/website/configuration/cookies_bar.html":
        "https://viindoo.com/documentation/20.0/applications/websites/website/publish/how-to-display-a-cookies-bar-on-your-website.html",
    /* website_payment */
    "/applications/finance/payment_providers.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    /* website_sale */
    "/applications/websites/website/configuration/address_autocomplete.html":
        "https://viindoo.com/documentation/20.0/applications/sales/ecommerce/getting-started/validate-customer-addresses-with-google-places.html",
    "/applications/websites/ecommerce/managing_products/variants.html":
        "https://viindoo.com/documentation/20.0/applications/getting-started/products/using-product-variants-in-viindoo.html",
    "/applications/sales/sales/products_prices/loyalty_discount.html":
        "https://viindoo.com/documentation/20.0/applications/sales/sales/gift/set-up-discount-and-loyalty-programs.html",
    "/applications/websites/ecommerce/ecommerce_management/order_handling.html#abandoned-cart":
        "https://viindoo.com/documentation/20.0/applications/sales/ecommerce/maximize-your-revenue/follow-up-abandoned-carts.html",
    "/applications/websites/ecommerce/google_merchant_center.html":
        "https://viindoo.com/documentation/20.0/applications/sales/ecommerce/maximize-your-revenue/publish-products-to-google-merchant-center.html",
    "/applications/websites/ecommerce/shipping.html#click-collect":
        "https://viindoo.com/documentation/20.0/applications/sales/ecommerce/maximize-your-revenue/let-customers-pick-up-orders-in-store.html",

    /* payment providers, localizations, mail servers, kiosk and website reporting */
    "/applications/finance/payment_providers/paypal.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/how-to-make-a-payment-with-paypal.html",
    "/applications/finance/payment_providers/razorpay.html#payment-providers-razorpay-recurring-payments":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/account-receivables/customer-payments/set-up-payment-service-providers-in-viindoo.html",
    "/applications/finance/fiscal_localizations/singapore.html": "",
    "/applications/finance/fiscal_localizations/hong_kong.html": "",
    "/applications/finance/fiscal_localizations/brazil.html": "",
    "/applications/finance/fiscal_localizations/india.html": "",
    "/applications/finance/fiscal_localizations/india.html#india-e-invoicing": "",
    "/applications/finance/fiscal_localizations/india.html#india-e-waybill": "",
    "/applications/finance/fiscal_localizations/india.html#india-gstr": "",
    "/applications/finance/fiscal_localizations/india.html#indian-check-gstin-status": "",
    "/applications/finance/fiscal_localizations/spain.html#veri-factu": "",
    "/applications/finance/fiscal_localizations/vietnam.html":
        "https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/fiscal-localizations/issue-e-invoice-by-integrating-viindoo-with-viettel-s-s-invoice-service.html",
    "/applications/general/email_communication/email_servers.html?highlight=outgoing email server#use-a-default-from-email-address":
        "https://viindoo.com/documentation/20.0/applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html",
    "/administration/on_premise/geo_ip.html":
        "https://viindoo.com/documentation/20.0/developer/development/cms-website-development.html",
    "/_downloads/eaa2883bd361273b475c9765f64e3e0c/pdfquotebuilderexamples.zip": "",
    "/applications/hr/attendances/hardware.html":
        "https://viindoo.com/documentation/20.0/applications/human-resources/attendances/operations/set-up-the-attendance-kiosk.html",
    "/applications/websites/website/reporting/plausible.html":
        "https://viindoo.com/documentation/20.0/applications/websites/website/optimize/how-to-track-your-website-s-traffic-with-plausible.html",
    "/developer/reference/backend/orm.html":
        "https://viindoo.com/documentation/20.0/developer/started/odoo-orm-basic.html",
    /* documentation pages of 20.0 that have no Viindoo counterpart */
    "/applications/finance/fiscal_localizations/austria.html#point-of-sale": "",
    "/applications/finance/fiscal_localizations/egypt.html": "",
    "/applications/finance/fiscal_localizations/malaysia.html#e-invoicing-integration-with-myinvois":
        "",
    "/applications/finance/fiscal_localizations/philippines.html": "",
    "/applications/finance/fiscal_localizations/united_states.html#pay-by-direct-deposit": "",
    "/applications/general/auth/2fa.html": "",
    "/applications/general/companies/multi_company.html#inter-company-clearing": "",
    "/applications/general/integrations/address_autocomplete.html": "",
    "/applications/inventory_and_mrp/inventory/shipping_receiving/setup_configuration.html": "",
    "/applications/inventory_and_mrp/purchase/manage_deals/calls_for_tenders.html": "",
    "/applications/sales/point_of_sale/payment_methods/terminals/dpo.html": "",
    "/applications/websites/website/configuration/spam_protection.html#website-spam-protection-cloudflare-turnstile":
        "",
    "/applications/websites/website/configuration/spam_protection.html#website-spam-protection-google-recaptcha":
        "",
    "/applications/websites/website/reporting/analytics.html#google-tag-manager": "",
};
