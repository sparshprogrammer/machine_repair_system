# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CreateJobCostAnalysisReport(models.TransientModel):
    _name = "create.job.cost.report"

    type = fields.Selection([('qweb-pdf', "PDF"),('qweb-html', "HTML"),], default='qweb-pdf', string="Type")

    def create_report(self):
        data = {
            'model': 'job.card',
            'form': self.read()[0]
        }
        data['form']['type'] = self.type
        job_cards = self.env["job.card"].search([])
        job_card_list = []
        for job in job_cards:
            material_cost = sum([line.material_cost_rate for line in job.job_card_lines])
            service_cost = sum([line.service_cost_rate for line in job.job_card_lines])
            job_card_list.append({
                'name': job.name, 'amount_total': job.amount_total,
                'material_cost': material_cost, 'service_cost': service_cost,
                'state': job.state
            })
        data["job_cards"] = job_card_list
        context = self.env.ref('machine_repair_system.job_cost_report').report_action(self, data=data)
        context["report_type"] = self.type
        print(context)
        return context
