odoo.define('viin_brand_event.settings', function(require) {
	"use strict";

	var BaseSettingRenderer = require('base.settings').Renderer;

	BaseSettingRenderer.include({

		_getAppIconUrl: function(module) {
			if (module == 'event') {
				return "/viin_brand_event/static/description/icon.png";
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