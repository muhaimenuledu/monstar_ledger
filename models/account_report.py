from odoo import models, fields
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    lead_reference = fields.Char("Opportunity ID MLES", readonly=True, copy=False)
    test_column = fields.Char("MLES", readonly=True, copy=False)