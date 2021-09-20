# -*- coding: utf-8 -*-
{
    "name": "POS Z Report || POS Session Report",
    "author": "Mohamed Sadiq",
    "version": "12.0.1.0",
    "website": "https://www.sadiq.ma",
    "category": "Point Of Sale",
    'summary': 'POS Z Report || POS Session Report',
    'description': """
    	POS Z Report || POS Session Report 
    """,
    "depends": [
        "base",
        "point_of_sale",
    ],
    "data": [
        "views/templates.xml",
        "report/report_pos_session.xml",
        "views/pos_session_view.xml",
    ],
    'demo': [],
    'test':[],
    "images": ["static/description/banner.jpg",],
    'license': 'AGPL-3',
    'currency':'USD',
    'price': 18.0,
    'qweb': [
        'static/src/xml/pos_session_report.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
