from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class Service(models.Model):
    _name = 'machine.service'

    name = fields.Char(string="Service")
    code = fields.Char(string="Code")
    rate = fields.Float(string="Rate", digits=dp.get_precision('Product Price'))
