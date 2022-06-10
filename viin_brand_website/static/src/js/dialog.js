odoo.define('viin_brand_website.Dialog', function(require) {
	"use strict";
	var Dialog = require('web.Dialog');

	Dialog.include({

		init: function (parent, options) {
			this._super(...arguments);
			this.title = this.title.replace(/Odoo/g,'Viindoo');
	    }
	});
	return Dialog;
});
