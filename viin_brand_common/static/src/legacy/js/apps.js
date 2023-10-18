/** @odoo-module **/

import apps from 'web.Apps';
import session from "web.session";
import framework from 'web.framework';
import {_t} from 'web.core';
import {patch} from "web.utils";
import config from "web.config";

var apps_client = null;

patch(apps.prototype, "viin_brand_common.apps", {
	/**
	 * @override
	 * Completely overide to add 'modules' in the client object
	 */
	get_client: function() {
		// return the client via a promise, resolved or rejected depending if
		// the remote host is available or not.
		var check_client_available = function(client) {
			var i = new Image();
			var def = new Promise(function (resolve, reject) {
				i.onerror = function() {
					reject(client);
				};
				i.onload = function() {
					resolve(client);
				};
			});
			i.src = _.str.sprintf('%s/to_base/static/description/main_screenshot.png', client.origin);
			return def;
		};
		if (apps_client) {
			return check_client_available(apps_client);
		} else {
			return this._rpc({model: 'ir.module.module', method: 'get_apps_server'})
				.then(function(u) {
					var link = $(_.str.sprintf('<a href="%s"></a>', u[0]))[0];
					var host = _.str.sprintf('%s//%s', link.protocol, link.host);
					var dbname = link.pathname;
					if (dbname[0] === '/') {
						dbname = dbname.substr(1);
					}
					var client = {
						origin: host,
						dbname: dbname
					};
					client.modules = u[1];
					apps_client = client;
					return check_client_available(client);
			});
		}
	},
	/**
	 * @override
	 * Completely overide to change the message noti and callback url
	 */
	start: function() {
		var self = this;
		return new Promise(function (resolve, reject) {
			self.get_client().then(function (client) {
				self.client = client;

				var qs = {};
				var u;
				if (self.remote_action_tag === 'loempia.embed.updates') {
					qs.modules = [client.modules];
					u = $.param.querystring(client.origin + "/apps/embed/client/update", qs);
				}else{
					qs.db = client.dbname;
					if (config.isDebug()) {
						qs.debug = odoo.debug;
					}
					u = $.param.querystring(client.origin + "/apps/embed/client", qs);
				}
				var css = {width: '100%', height: '750px'};
				self.$ifr = $('<iframe>').attr('src', u);

				self.uniq = _.uniqueId('apps');
				$(window).on("message." + self.uniq, self.proxy('_on_message'));

				self.on('message:ready', self, function(m) {
					var w = this.$ifr[0].contentWindow;
					var act = {
						type: 'ir.actions.client',
						tag: this.remote_action_tag,
						params: _.extend({}, this.params, {
							db: session.db,
							origin: session.origin,
						})
					};
					w.postMessage({type:'action', action: act}, client.origin);
				});

				self.on('message:set_height', self, function(m) {
					this.$ifr.height(m.height);
				});

				self.on('message:blockUI', self, function() { framework.blockUI(); });
				self.on('message:unblockUI', self, function() { framework.unblockUI(); });
				self.on('message:warn', self, function(m) {self.displayNotification({ title: m.title, message: m.message, sticky: m.sticky, type: 'danger' }); });

				self.$ifr.appendTo(self.$('.o_content')).css(css).addClass('apps-client');

				resolve();
			}, function() {
				self.displayNotification({ title: _t('Viindoo Marketplace will be available soon'), message: _t('Showing locally available modules'), sticky: true, type: 'danger' });
				return self._rpc({
					route: '/web/action/load',
					params: {action_id: self.failback_action_id},
				}).then(function(action) {
					return self.do_action(action, {clear_breadcrumbs: true});
				}).then(resolve, reject);
			});
		});
	}
});
