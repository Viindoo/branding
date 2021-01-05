odoo.define('viin_brand_contacts.settings', function(require) {
	"use strict";

	var BaseSettingRenderer = require('base.settings').Renderer;

	BaseSettingRenderer.include({

		_getAppIconUrl: function(module) {
			if (module == 'contacts') {
				return "/viin_brand_contacts/static/description/icon.png";
			}
			else if (module == 'general_settings') {
				return "/viin_brand_base/static/description/settings.png";
			}
			else {
				return this._super.apply(this, arguments);
			}
		}
	});
});