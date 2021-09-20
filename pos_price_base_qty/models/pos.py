# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, _


class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_price_base_qty = fields.Boolean('Allow Price Based Qty', default=True)

