
{
    'name': 'Pos Reports',
    'category': 'Point of Sale',
    'summary': 'Allow user to print X-Report, Z-Report and Sales Summary report.',
    'description': """
Allow user to print X-Report, Z-Report and Sales Summary report.
""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "http://www.acespritech.com",
    'price': 40.00, 
    'currency': 'EUR',
    'version': '1.0',
    'depends': ['point_of_sale', 'base'],
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'reports.xml',
        'views/aspl_pos_report.xml',
        'views/pos_sales_report_template.xml',
        'views/pos_sales_report_pdf_template.xml',
        'views/sales_details_pdf_template.xml',
        'views/sales_details_template.xml',
        'views/front_sales_report_pdf_template.xml',
        'views/front_sales_thermal_report_template.xml',
        'views/res_users_view.xml',
        'wizard/wizard_pos_sale_report_view.xml',
        'wizard/wizard_sales_details_view.xml',
        'wizard/wizard_pos_x_report.xml',
        'data/email_cron.xml',
        'data/email_cron'
    ],
    'installable': True,
    'auto_install': False,
}


