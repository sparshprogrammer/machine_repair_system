from odoo import models, fields, api, _


class Product(models.Model):
    _inherit = 'product.template'

    is_machine = fields.Boolean(string="Is Machine?")
    is_material = fields.Boolean(string="Is Material?")