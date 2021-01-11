odoo.define('viin_brand.settings', function(require) {
    "use strict";

    var BaseSettingRenderer = require('base.settings').Renderer;

    BaseSettingRenderer.include({
        _getAppIconUrl: function(module) {
			function checkFileExists(url){
				var http = new XMLHttpRequest();
				http.open('HEAD', url, false);
				http.send();
				return http.status != 404;
				}
			
			var module_icon = "/viin_brand/static/img/" + module + ".png";
			
			if (module == 'general_settings') {
	    		return "/viin_brand/static/img/settings.png";
			} else if (checkFileExists(module_icon)){
                return module_icon;
            }
			return this._super.apply(this, arguments);
		}
	});
});
