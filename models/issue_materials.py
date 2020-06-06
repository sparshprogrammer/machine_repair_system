from odoo import models, api, fields, _


class IssueMaterial(models.Model):
    _name = 'issue.material'
    _rec_name = 'voucher_no'

    voucher_no = fields.Char(string="Voucher Number", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _("New"))
    job_card = fields.Many2one("job.card", string="Job Card", required=True)
    job_card_line = fields.Many2one("job.card.line", string="Job Card Line")
    date = fields.Datetime(string="Date of Issue")
    material = fields.Many2one("product.template", string="Material", domain="[('is_material', '=', True)]")
    qty = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")

    @api.model
    def create(self, values):
        if values.get('voucher_no', _('New')) == _('New'):
            values['voucher_no'] = self.env['ir.sequence'].next_by_code('issue.material') or _('New')
        res = super(IssueMaterial, self).create(values)
        job_card = self.env['job.card'].search([('id', '=', res.job_card.id)])
        job_card.job_card_material_lines = [(0, 0, {'job_card_line_id': res.job_card_line, 'material': res.material,
                                                    'quantity': res.qty, 'unit_price': res.unit_price})]
        self.env["delivery.note"].create({
            "job_card": res.job_card.id,
            "job_card_line": res.job_card_line.id,
            "material": res.material.id,
            "qty": res.qty,
            "reference": res.voucher_no
        })
        # method = self.env["stock.picking.type"].search([("name", "ilike", "Delivery")])
        # location_customer, loc_vendor = self.env['stock.warehouse']._get_partner_locations()
        # stock_picking = self.env["stock.picking"].create({
        #     "partner_id": res.job_card.client.id,
        #     "picking_type_id": method.id,
        #     "location_id": method.default_location_src_id.id,
        #     "location_dest_id": location_customer.id
        # })
        # print(stock_picking)
        return res

    @api.multi
    @api.depends("job_card")
    def onchange_job_card_line(self):
        self.job_card_line = self.env['job.card.line'].search([('job_card_id', '=', self.job_card)])

    @api.multi
    @api.onchange("material")
    def onchange_material(self):
        self.unit_price = self.material.list_price

