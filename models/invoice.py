from odoo import fields, models, api, _


class ExtInvoice(models.Model):
    _inherit = 'account.invoice'

    job_card = fields.Many2one("job.card", string="Job Card")
