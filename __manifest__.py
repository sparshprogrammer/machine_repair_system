# -*- coding: utf-8 -*-
{
    'name': "machine_repair_system",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '4.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/quotation_view.xml',
        'views/job_card_view.xml',
        'views/service_view.xml',
        'views/product.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/quotation_report.xml',
        'views/issue_materials.xml',
        'views/issue_materials_print.xml',
        'views/delivery_note.xml',
        'views/invoice_view.xml',
        'views/job_cost_analysis_report.xml',
        'views/job_card_report.xml',
        'wizards/report_job_cost_analysis.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}