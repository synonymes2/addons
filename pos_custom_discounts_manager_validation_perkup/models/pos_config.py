# -*- coding: utf-8 -*-

from odoo import fields, models


class POSConfig(models.Model):
    _inherit = 'pos.config'

    iface_validate_custom_discounts = fields.Boolean(string='Enable Validation for Custom Discounts')

