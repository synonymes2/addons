# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_modifiers = fields.Boolean('Allow Modifiers', default=True)

class product_modifiers(models.Model):
    _name = 'product.modifiers'

    product_id = fields.Many2one('product.product','Product')
    product_ids = fields.Many2one('product.product','Product')
    amount = fields.Float("Amount")
    qty = fields.Float("Quantity",default=1)

class product_product(models.Model):
    _inherit = 'product.product'
    
    has_modifier = fields.Boolean('Has Modifier')
    modifiers_id = fields.One2many('product.modifiers','product_ids')
    



