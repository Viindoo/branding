/** @odoo-module **/

import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";


/* Define documentation of odoo which will be replaced by Viindoo one on setting pages only,
if none found the system will fallback to the original one of odoo
This approach help we manage nearly all odoo documentation to be replaced or not
 */
const ODOO_VIINDOO_DOCUMENTATION_MAPPING = {
	/* account */
	"/applications/finance/fiscal_localizations.html": undefined,
	"/applications/finance/accounting/taxation/taxes/default_taxes.html": undefined,
	"/applications/finance/accounting/taxation/taxes/taxcloud.html": undefined,
	"/applications/finance/accounting/taxation/taxes/avatax.html": undefined,
	"/applications/finance/accounting/taxation/taxes/eu_distance_selling.html": undefined, // in v17 "/applications/finance/accounting-and-invoicing/taxation/distance-selling-for-eu-intra-community.html"
	"/applications/finance/accounting/taxation/taxes/cash_basis_taxes.html": undefined,
	"/applications/finance/accounting/others/multi_currency.html": undefined,
	"/applications/finance/accounting/receivables/customer_invoices/snailmail.html": undefined,
	"/applications/sales/sales/send_quotations/different_addresses.html": undefined, // in v17 /applications/sales/sales/send-quotations/manage-invoicing-address-and-delivery-address-in-sales.html
	"/applications/finance/accounting/receivables/customer_invoices/cash_rounding.html": undefined,
	"/applications/finance/accounting/reporting/declarations/intrastat.html": undefined,
	"/applications/finance/accounting/receivables/customer_payments/online_payment.html": undefined,
	"/applications/finance/accounting/receivables/customer_payments/batch.html": undefined,
	"/applications/finance/accounting/receivables/customer_payments/batch_sdd.html": undefined,
	"/applications/finance/accounting/receivables/customer_invoices/epc_qr_code.html": undefined,
	"/applications/finance/accounting/payables/pay/check.html": undefined,
	"/applications/finance/accounting/payables/pay/sepa.html": undefined,
	"/applications/finance/accounting/payables/supplier_bills/invoice_digitization.html": undefined,
	"/applications/finance/accounting/others/analytic_accounting.html": undefined,
	"/applications/finance/accounting/others/adviser/budget.html": undefined,
	/* auth_oauth */
	"/applications/general/auth/google.html": undefined, // in v17 /applications/getting-started/system-settings/sign-in-with-google-authentication.html
	/* base_setup */
	"/applications/marketing/sms_marketing/pricing/pricing_and_faq.html": undefined,
	"/applications/general/export_import_data.html": undefined, // in v17 /applications/getting-started/guiding-to-import-and-export-data.html#import-data-into-viindoo-software
	"/applications/productivity/mail_plugins.html": undefined, // in v17 /applications/getting-started.html
	"/applications/general/auth/ldap.html": undefined, // in v17 /applications/getting-started/external-apps-integration/ldap.html?highlight=ldap
	"/applications/websites/website/optimize/unsplash.html": undefined, // in v17 /applications/websites/website/optimize/how-to-intergrate-with-free-image-library-at-unsplash.html
	/* base_vat */
	"/applications/finance/accounting/taxation/taxes/vat_validation.html": undefined,
	/* calendar */
	"/applications/productivity/calendar/outlook.html": undefined, // in v17 /applications/productivity/calendar/sychronization-with-outlook-s-calendar.html
	"/applications/productivity/calendar/google.html": undefined, // in v17 /applications/productivity/calendar/sychronization-with-google-s-calendar.html
	/* crm */
	"/applications/sales/crm/track_leads/lead_scoring.html#assign-leads": undefined,
	"/applications/sales/crm/acquire_leads/lead_mining.html": undefined,
	/* digest */
	"/applications/general/digest_emails.html": undefined,
	/* event */
	/* hr_recruitment */
	/* hr_timesheet */
	"/applications/services/timesheets/overview/time_off.html": undefined,
	/* iap */
	"/applications/general/in_app_purchase.html": undefined,
	/* mail */
	"/applications/general/email_communication/email_servers.html": undefined, // in v17 /applications/getting-started/system-settings/how-to-set-mail-server-for-sending-receiving-emails-in-viindoo.html
	"/applications/general/email_communication/email_domain.html#be-spf-compliant": undefined,
	/* mrp */
	"/applications/inventory_and_mrp/manufacturing/management/bill_configuration.html#adding-a-routing": undefined, // in v17 /applications/supply-chain/manufacturing/products/how-to-create-bills-of-materials.html
	"/applications/inventory_and_mrp/manufacturing/management/subcontracting.html": undefined, // in v17 /applications/supply-chain/manufacturing/operations/manage-subcontracts-in-your-manufacturing-proccess.html
	"/applications/inventory_and_mrp/manufacturing/management/use_mps.html": undefined, // in v17 /applications/supply-chain/manufacturing/planning/how-to-use-the-master-production-schedule-in-viindoo.html
	"/applications/inventory_and_mrp/inventory/management/planning/scheduled_dates.html": undefined, // in v17 /applications/supply-chain/inventory/warehouse-management/planning/understanding-the-scheduled-delivery-date-computation.html
	/* point_of_sale */
	"/applications/sales/point_of_sale/pricing/cash_rounding.html": undefined, // in v17 /applications/finance/accounting-and-invoicing/account-receivables/customer-invoices/settings/configure-cash-rounding-method.html
	"/applications/sales/point_of_sale/payment_methods/terminals/vantiv.html": undefined, // in v17 /applications/sales/point-of-sale/pricing-features/payment-with-vantiv-payment-terminal-in-pos.html
	"/applications/sales/point_of_sale/payment_methods/terminals/six.html": undefined, // in v17 /applications/sales/point-of-sale/pricing-features/payment-with-six-payment-terminal-in-pos.html
	/* product */
	"/applications/sales/sales/products_prices/products/product_images.html": undefined,
	/* purchase */
	"/applications/inventory_and_mrp/purchase/manage_deals/agreements.html": undefined,
	"/applications/inventory_and_mrp/purchase/manage_deals/control_bills.html": undefined,
	"/applications/inventory_and_mrp/inventory/management/products/uom.html": undefined,
	/* purchase_stock */
	"/applications/inventory_and_mrp/inventory/shipping/operation/dropshipping.html": undefined,
	/* sale */
	"/applications/sales/sales/products_prices/products/variants.html": undefined,
	"/applications/sales/sales/products_prices/prices/pricing.html": undefined,
	"/applications/inventory_and_mrp/inventory/shipping/setup/third_party_shipper.html": undefined,
	"/applications/sales/sales/invoicing/invoicing_policy.html": undefined,
	"/applications/sales/sales/invoicing/down_payment.html": undefined,
	"/applications/sales/sales/amazon_connector/setup.html": undefined,
	/* sale_management */
	"/applications/sales/sales/send_quotations/quote_template.html": undefined,
	/* sale_pdf_quote_builder */
	"/applications/sales/sales/send_quotations/pdf_quote_builder.html": undefined,
	/* sale_stock */
	"/applications/inventory_and_mrp/inventory/management/planning/scheduled_dates.html": undefined,
	/* stock */
	"/applications/inventory_and_mrp/inventory/management/products/usage.html#packages": undefined,
	"/applications/inventory_and_mrp/inventory/management/misc/batch_transfers.html": undefined,
	"/applications/inventory_and_mrp/manufacturing/management/quality_control.html": undefined,
	"/applications/inventory_and_mrp/inventory/barcode/setup/software.html": undefined,
	"/applications/inventory_and_mrp/inventory/management/products/usage.html#packaging": undefined,
	"/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/differences.html": undefined,
	"/applications/inventory_and_mrp/inventory/management/lots_serial_numbers/expiration_dates.html": undefined,
	"/applications/inventory_and_mrp/inventory/management/misc/owned_stock.html": undefined,
	"/applications/inventory_and_mrp/inventory/management/warehouses/warehouses_locations.html": undefined,
	"/applications/inventory_and_mrp/inventory/routes/concepts/use_routes.html": undefined,
	"/applications/inventory_and_mrp/inventory/management/delivery/dropshipping.html": undefined,
	/* stock_account */
	"/applications/inventory_and_mrp/inventory/management/reporting/integrating_landed_costs.html": undefined,
	/* web_unsplash */
	"/applications/websites/website/optimize/unsplash.html#generate-an-unsplash-access-key": undefined,
	/* website */
	"/applications/websites/website/configuration/cookies_bar.html": undefined,
	/* website_sale */
};

patch(DocumentationLink.prototype, {
	get url() {
		let original_url = super.url;
		// if url contain viindoo, return
		if (original_url.includes("viindoo.com")){
			return original_url;
		}
		const serverVersion = session.server_version_info.includes("final");
		const odooDocumentation = "https://www.odoo.com/documentation/" + serverVersion;
		const viindooDocumentation = "https://viindoo.com/documentation/" + serverVersion;
		let odoo_url = original_url.replace(odooDocumentation, '');
		if (ODOO_VIINDOO_DOCUMENTATION_MAPPING[odoo_url]){
			return viindooDocumentation + ODOO_VIINDOO_DOCUMENTATION_MAPPING[odoo_url];
		}
		return original_url;
	}
});
