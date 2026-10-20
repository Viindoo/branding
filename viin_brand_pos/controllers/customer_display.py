from odoo import http
from odoo.http import request

from odoo.addons.point_of_sale.controllers.customer_display import PosCustomerDisplay


class PosCustomerDisplayBrand(PosCustomerDisplay):

    @http.route()
    def pos_customer_display(self, id_, device_uuid, **kw):
        response = super().pos_customer_display(id_, device_uuid, **kw)
        # Web translations follow user_context['lang'], which core takes from the public user, not
        # from the visitor's language (request.lang). A logged-in user keeps their own language.
        # A NotFound response has no qcontext.
        session_info = (getattr(response, 'qcontext', None) or {}).get('session_info')
        if session_info and request.env.user._is_public():
            session_info['user_context'] = {**session_info['user_context'], 'lang': request.lang.code}
        return response
