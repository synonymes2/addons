# -*- coding: utf-8 -*-
{
    'name': 'POS Custom Discounts Manager Validation',
    'version': '1.0',
    'summary': 'POS Custom Discounts Manager Validation',
    'description': """
POS Custom Discounts Manager Validation
=======================================

This module allows manager validation for POS custom discounts
""",
    'category': 'Point of Sale',
    'author': 'PerkUp',
    'contributors': ['Michael Aldrin C. Villamar'],
    'website': 'https://www.perkup.pk',
    'depends': [
        'pos_custom_discounts',
        'pos_manager_validation_mac5',
    ],
    'data': [
        'views/pos_manager_validation_templates.xml',
        'views/pos_config_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

