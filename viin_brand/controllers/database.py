from odoo.addons.web.controllers.main import Database as DB


class Database(DB):

    def _render_template(self, **d):
        res = super(Database, self)._render_template()
        if res:
            res = res.replace('Odoo', 'Viindoo') \
                     .replace('https://www.odoo.com/privacy', 'https://viindoo.com/policy/privacy-policy') \
                     .replace('/web/static/img/logo2.png', '/viin_brand/static/img/Viindoo-logo.svg') \
                     .replace('img-fluid d-block mx-auto', 'img-fluid d-block mx-auto my-4') \
                     .replace('/web/static/img/favicon.ico', '/viin_brand/static/img/favicon.ico')
        return res
