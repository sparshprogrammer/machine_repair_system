from odoo import fields, models, api, _

class DeliveryNote(models.Model):
    _name = "delivery.note"

    date = fields.Datetime(string="Date of Delivery")
    job_card = fields.Many2one("job.card", string="Job Card", required=True)
    job_card_line = fields.Many2one("job.card.line", string="Job Card Line")
    reference = fields.Char(string="Reference")
    material = fields.Many2one("product.template", string="Material", domain="[('is_material', '=', True)]")
    qty = fields.Float(string="Quantity")
