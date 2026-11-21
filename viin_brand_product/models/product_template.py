from odoo import _, api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.readonly
    def action_open_documents(self):
        """Drop the link to the downloadable examples, which are hosted by Odoo, from the empty-state help."""
        action = super().action_open_documents()
        action['help'] = """
                <p class="o_view_nocontent_smiling_face">
                    %s
                </p>
                <p>
                    %s
                    <br/>
                    %s
                </p>
            """ % (
            _("Upload files to your product"),
            _("Use this feature to store any files you would like to share with your customers"),
            _("(e.g: product description, ebook, legal notice, ...)."),
        )
        return action
