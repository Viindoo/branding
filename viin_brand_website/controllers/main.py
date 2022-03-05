from odoo import http
from odoo.addons.website.controllers.main import Website



class WebsiteInherit(Website):

    @http.route('/website/info', type='http', auth="public", website=True, sitemap=True)
    def website_info(self, **kwargs):
        landing_page = {
            'website': 'https://viindoo.com/intro/website',
            'mail': 'https://viindoo.com/intro/discuss',
            'to_account_accountant': 'https://viindoo.com/intro/accounting',
            'account' : 'https://viindoo.com/intro/invoicing',
            'hr': 'https://viindoo.com/intro/employees',
            'stock': 'https://viindoo.com/intro/inventory',
            'contacts': 'https://viindoo.com/intro/contact',
            'project': 'https://viindoo.com/intro/project',
            'crm': 'https://viindoo.com/intro/crm',
            'survey': 'https://viindoo.com/intro/survey',
            'mrp': 'https://viindoo.com/intro/mrp',
            'hr_recruitment': 'https://viindoo.com/intro/recruitment',
            'sale_management': 'https://viindoo.com/intro/sales',
            'website_slides': 'https://viindoo.com/intro/e-learning',
            'calendar' : 'https://viindoo.com/intro/calendar',
            'to_hr_employee_advance': 'https://viindoo.com/intro/employee-advance',
            'hr_expense' : 'https://viindoo.com/intro/expense',
            'website_sale': 'https://viindoo.com/intro/ecommerce',
            'point_of_sale' : 'https://viindoo.com/intro/pos',
            'website_blog': 'https://viindoo.com/intro/blogs',
            'mass_mailing': 'https://viindoo.com/intro/email-marketing',
            'mass_mailing_sms': 'https://viindoo.com/intro/sms-marketing',
            'hr_timesheet': 'https://viindoo.com/intro/timesheet',
            'note': 'https://viindoo.com/intro/notes',
            'board': 'https://viindoo.com/intro/dashboards',
            'website_forum': 'https://viindoo.com/intro/app-forum',
            'to_hr_payroll': 'https://viindoo.com/intro/payroll',
            'hr_holidays': 'https://viindoo.com/intro/time-off',
            'to_okr': 'https://viindoo.com/intro/okr',
            'maintenance': 'https://viindoo.com/intro/maintenance',
            'fleet': 'https://viindoo.com/intro/fleet',
            'to_hr_meal': 'https://viindoo.com/intro/hr-meal',
            'repair': 'https://viindoo.com/intro/repair',
            'im_livechat': 'https://viindoo.com/intro/live-chat',
            'viin_social': 'https://viindoo.com/intro/social-marketing',
            'to_loan_management': 'https://viindoo.com/intro/loan-management',
            'viin_hr_overtime': 'https://viindoo.com/intro/overtime',
        }
        res = super(WebsiteInherit, self).website_info(**kwargs)
        apps = res.qcontext.get('apps')
        for app in apps:
            if app.name in landing_page:
                app.website = landing_page.get(app.name,'')
        return res
