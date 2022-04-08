odoo.define('viin_brand_website.Dialog', function(require) {
	"use strict";
	var Dialog = require('web.Dialog');
	var core = require('web.core');
	var _t = core._t;

	Dialog.include({

		init: function (parent, options) {
			this._super(...arguments);
			this.title = _t('Viindoo');
	    }
	});
	return Dialog;
});
