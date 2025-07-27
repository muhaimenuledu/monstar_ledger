from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        compute='_compute_product_fields',
        store=True
    )

    product_name = fields.Char(
        string='Product Name',
        compute='_compute_product_fields',
        store=True
    )

    @api.depends('product_id')
    def _compute_product_fields(self):
        for line in self:
            if line.product_id:
                line.product_category_id = line.product_id.categ_id
                line.product_name = line.product_id.display_name
            else:
                line.product_category_id = False
                line.product_name = False
