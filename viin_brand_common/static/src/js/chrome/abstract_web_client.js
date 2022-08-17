odoo.define('viin_brand_common.AbstractWebClient', function (require) {
"use strict";

var AbstractWebClient = require("web.AbstractWebClient");

	AbstractWebClient.include({
		init: function (parent, options) {
			this._super(...arguments);
			this.set('title_part', {"zopenerp": "Viindoo"});
	    }
	});
	return AbstractWebClient;
});
