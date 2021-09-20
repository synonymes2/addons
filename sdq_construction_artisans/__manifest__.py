# -*- coding: utf-8 -*-
{
    'name': "sdq_construction_artisans",


    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Mohamed Sadiq",
    'website': "http://www.yourcompany.com",
    'category': 'project management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/ir_sequence_data.xml',
        'report/report.xml',
        'report/artisan_report.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}