odoo.define('viin_brand.settings', function(require) {
    "use strict";

    var BaseSettingRenderer = require('base.settings').Renderer;

    BaseSettingRenderer.include({
		_renderTabs: function () {
			var self = this;
			self._super.apply(self, arguments);
			
			_.each(self.modules, function(module){
				var module_icon = module.key == 'general_settings' ? '/viin_brand/static/img/apps/settings.png' : '/viin_brand/static/img/apps/' + module.key + '.png';
				self._rpc({
					model: 'res.config.settings',
					method: 'check_file_exists',
					args: [module_icon],
				})
				.then(function(result){
					if (result){
						module.imgurl = module_icon;
						self.$('.tab[data-key="' + module.key + '"] > div').attr('style', `background : url("${module.imgurl}") no-repeat center;background-size:contain;`);
					}
				});
			});
    	},
	});
});
