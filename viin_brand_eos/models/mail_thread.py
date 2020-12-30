from lxml import html as htmlformat
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _replace_local_links(self, html, base_url=None):        
        """
        search all element, it have ``Odoo`` in text. Check ``www.odoo.com``
        in link href of element. If true, allow set up href is ``https://viindoo.com``
        and text content is Viindoo EOS    
        """
        html = super()._replace_local_links(html, base_url=base_url)
        key_odoo = "Odoo"
        if key_odoo not in html: 
            return html
        html_format = htmlformat.fromstring(html)
        odoo_elements = html_format.xpath("//*[text()[contains(.,'%s')]]" % key_odoo)
        for element in odoo_elements:
            # check current element
            if "www.odoo.com" in element.get("href", ""):
                element.set("href", "https://viindoo.com")
                element.text = "Viindoo EOS"
            # check child element   
            for element_child in element.getchildren():
                if "www.odoo.com" in element_child.get("href", ""):
                    element.set("href", "https://viindoo.com")
                    element_child.text = "Viindoo EOS"
        return htmlformat.tostring(html_format).decode("utf-8")    
    
