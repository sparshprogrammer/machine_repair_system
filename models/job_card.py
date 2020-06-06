from _datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, _

JOB_PRIORITIES = [('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')]


class JobCard(models.Model):
    _name = 'job.card'

    # Client related fields
    client = fields.Many2one('res.partner', string='Client', required=True)
    client_email = fields.Char(string='Client Email')
    client_mobile = fields.Char(string='Client Mobile')
    client_phone = fields.Char(string='Client Phone')
    origin = fields.Char(string='Quotation No.', readonly=True)

    # Machine related fields
    machine = fields.Many2one('product.template', string='Machine')
    machine_brand = fields.Char(string='Machine Brand')
    machine_model = fields.Char(string='Machine Model')

    problem = fields.Char(string="Problem")
    state = fields.Selection([
        ('quotation', 'Quotation'),
        ('job_card', 'Job Card'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='quotation')
    name = fields.Char(string="Job Card No.", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    job_card_lines = fields.One2many('job.card.line', 'job_card_id', string="Machines")
    job_card_material_lines = fields.One2many('job.card.material.line', 'job_card_material_id', string="Material")
    job_card_worked_hours_lines = fields.One2many("job.card.worked.hours.line", "job_card_id", string="Worked Hours")
    job_card_sub_contract = fields.One2many("job.card.subcontract", "job_card_id", string="Sub Contract")
    assigned_ids = fields.Many2many('res.partner', string="Assigned Employees")
    priority = fields.Selection(JOB_PRIORITIES, 'Priority', default='1')
    material_amount = fields.Float(string="Material Amount", readonly=True, compute="_get_material_amount",
                                   digits=dp.get_precision('Product Price'))
    service_amount = fields.Float(string="Service Amount", readonly=True, compute="_get_service_amount",
                                  digits=dp.get_precision('Product Price'))
    amount_untaxed = fields.Float(string="Untaxed Amount", readonly=True, compute="_get_untaxed_total",
                                  digits=dp.get_precision('Product Price'))
    amount_tax = fields.Float(string="Tax Amount", readonly=True, compute="_get_taxed_total",
                              digits=dp.get_precision('Product Price'))
    amount_total = fields.Float(string="Total", readonly=True, compute="_get_total",
                                digits=dp.get_precision('Product Price'))
    description = fields.Text(string="Description")

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('job.card') or _('New')
        res = super(JobCard, self).create(values)
        return res

    @api.onchange("client")
    def onchange_client(self):
        print("Here")
        self.client_email = self.client.email
        self.client_mobile = self.client.mobile
        self.client_phone = self.client.phone

    @api.multi
    @api.depends("job_card_lines.material_cost_rate")
    def _get_material_amount(self):
        for rec in self:
            total = 0
            for line in rec.job_card_lines:
                total += line.material_cost_rate
            rec.material_amount = total

    @api.multi
    @api.depends("job_card_lines.service_cost_rate")
    def _get_service_amount(self):
        for rec in self:
            total = 0
            for line in rec.job_card_lines:
                total += line.service_cost_rate
            rec.service_amount = total

    @api.one
    @api.depends("job_card_lines.price_subtotal_with_tax", "job_card_lines.price_subtotal_without_tax")
    def _get_untaxed_total(self):
        total = 0
        for lines in self.job_card_lines:
            total += lines.price_subtotal_without_tax
        self.amount_untaxed = total

    @api.one
    @api.depends("job_card_lines.price_subtotal_with_tax", "job_card_lines.price_subtotal_without_tax")
    def _get_total(self):
        total = 0
        for lines in self.job_card_lines:
            total += lines.price_subtotal_with_tax
        self.amount_total = total

    @api.one
    @api.depends("amount_untaxed", "amount_total")
    def _get_taxed_total(self):
        self.amount_tax = self.amount_total - self.amount_untaxed

    @api.one
    def set_to_quotation(self):
        self.write({
            'state': 'quotation'
        })

    @api.one
    def assign_job_card(self):
        self.write({
            'state': 'job_card'
        })

    @api.one
    def job_done(self):
        self.write({
            'state': 'done'
        })

    @api.one
    def cancel_job(self):
        self.write({
            'state': 'cancel'
        })


class JobCardLines(models.Model):
    _name = "job.card.line"

    name = fields.Char(string="Job Line Reference", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    job_card_id = fields.Many2one('job.card')
    machine = fields.Many2one('product.template', string="Machine Name", required=True,
                              domain="[('is_machine','=', True)]")
    qty = fields.Integer(string="Quantity")

    worker = fields.Many2one("res.partner", string="Workers")
    problem = fields.Char(string="Problem")
    status = fields.Selection([
        ('quotation', 'Quotation'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='quotation')
    taxes_id = fields.Many2many('account.tax', string="Taxes")
    price_subtotal_with_tax = fields.Float(string="Subtotal", compute="_get_total",
                                           digits=dp.get_precision('Product Price'))
    price_subtotal_without_tax = fields.Float(string="Subtotal Without tax", compute="_get_total",
                                              digits=dp.get_precision('Product Price'))
    material_cost_rate = fields.Float(string="Material Cost Rate", compute="_get_material_cost",
                                      digits=dp.get_precision('Product Price'))
    service_cost_rate = fields.Float(string="Service Cost Rate", compute="_get_service_cost",
                                     digits=dp.get_precision('Product Price'))

    @api.depends("material_cost_rate", "service_cost_rate")
    def _get_total(self):
        for rec in self:
            rec.price_subtotal_without_tax = rec.qty * (rec.service_cost_rate + rec.material_cost_rate)
            rec.price_subtotal_with_tax = rec.taxes_id.compute_all(rec.price_subtotal_without_tax)['total_included']

    @api.depends("job_card_id.job_card_worked_hours_lines")
    def _get_service_cost(self):
        for rec in self:
            total_cost = 0
            for line in rec.job_card_id.job_card_worked_hours_lines:
                if line.job_card_line_id.id == rec.id:
                    total_cost += line.total_price
            rec.service_cost_rate = total_cost

    @api.depends("job_card_id.job_card_material_lines")
    def _get_material_cost(self):
        for rec in self:
            total_cost = 0
            for line in rec.job_card_id.job_card_material_lines:
                if line.job_card_line_id.id == rec.id:
                    total_cost += line.total_price
            rec.material_cost_rate = total_cost

    @api.depends("machine", "qty", "total_price")
    def price_job_card(self):
        job_card_line = self.env["job.card.line"].search([("id", '=', self.job_card_id)])

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('job.card.line') or _('New')
        res = super(JobCardLines, self).create(values)
        return res

    @api.one
    def set_in_progress(self):
        if self.job_card_id.state == 'job_card':
            self.write({
                'status': 'in_progress'
            })

    @api.one
    def set_done(self):
        self.write({
            'status': 'done'
        })

    @api.one
    def set_cancel(self):
        self.write({
            'status': 'cancel'
        })


class JobCardMaterialLine(models.Model):
    _name = 'job.card.material.line'

    job_card_material_id = fields.Many2one("job.card", readonly=True)
    job_card_line_id = fields.Many2one("job.card.line", string="Job Card Line", readonly=True)
    machine = fields.Many2one('product.template', string="Machine", readonly=True)
    material = fields.Many2one('product.template', string="Material", domain="[('is_material', '=', True)]", readonly=True)
    quantity = fields.Integer(string="Quantity", readonly=True)
    unit_price = fields.Float(string="Unit Price", digits=dp.get_precision('Product Price'), readonly=True)
    total_price = fields.Float(string="Total Price", compute="_calculate_price", readonly=True,
                               digits=dp.get_precision('Product Price'))

    @api.depends("unit_price", "material", "quantity", "total_price")
    def price_job_card(self):
        job_card_line = self.env["job.card.line"].search([("id", '=', self.job_card_material_id)])
        print(job_card_line)
        job_card_line.material_cost_rate = self.total_price

    @api.onchange("job_card_line_id")
    def onchange_job_card_line_id(self):
        if len(self.job_card_material_id.job_card_lines) == 0:
            return {'warning': {
                'title': 'Warning',
                'message': 'Create Job Card Lines first.'
            }
            }

    @api.depends("material", "quantity", "unit_price")
    def _calculate_price(self):
        for rec in self:
            rec.total_price = rec.unit_price * rec.quantity

    @api.onchange("material")
    def onchange_material(self):
        self.unit_price = self.material.standard_price

    @api.onchange("job_card_line_id")
    def onchange_job_card_line(self):
        self.machine = self.job_card_line_id.machine


class JobCardWorkedHoursLine(models.Model):
    _name = "job.card.worked.hours.line"

    job_card_line_id = fields.Many2one("job.card.line")
    job_card_id = fields.Many2one("job.card")
    date = fields.Datetime(sting="Date", default=datetime.now())
    machine = fields.Many2one('product.template', string="Machine")
    technician = fields.Many2one('res.partner', string="Technician")
    service = fields.Many2one('machine.service', string="Service")
    rate_of_service = fields.Float(string="Rate of Service", digits=dp.get_precision('Product Price'))
    hours = fields.Float(string="Hours")
    total_price = fields.Float(string="Total Price", compute="_compute_total_price",
                               digits=dp.get_precision('Product Price'))

    @api.onchange("job_card_line_id")
    def onchange_job_card_line_id(self):
        if len(self.job_card_id.job_card_lines) == 0:
            return {'warning': {
                'title': 'Warning',
                'message': 'Create Job Card Lines first.'
            }
            }

    @api.depends("rate_of_service", "hours")
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.rate_of_service * rec.hours

    @api.onchange("service")
    def _onchange_service(self):
        self.rate_of_service = self.service.rate

    @api.onchange("job_card_line_id")
    def onchange_job_card_line(self):
        self.machine = self.job_card_line_id.machine


class JobCardSubContract(models.Model):
    _name = "job.card.subcontract"

    job_card_id = fields.Many2one("job.card", string="Job Card")
    vendor = fields.Many2one("res.partner", string="Vendor", domain="[('supplier', '=', True)]")
    material = fields.Many2one("product.template", string="Material", domain="[('is_material', '=', True)]")
    qty = fields.Float(string="Quantity")
    bill_created = fields.Boolean(string="Bill Created ?")

    @api.one
    def create_bill(self):
        invoice = self.env["account.invoice"].create({
            "job_card": self.job_card_id.id,
            "partner_id": self.vendor.id,
            "type": "in_invoice",
            "invoice_line_ids": [(0, 0, {
                "product_id": self.material.id,
                "name": self.material.name,
                "quantity": self.qty,
                "price_unit": self.material.list_price,
                "account_id": 20
            })]
        })
        if invoice:
            self.bill_created = True
