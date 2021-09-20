# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class test_Database_002(models.Model):
    _name = 'test_Database_002.test_Database_002'

    name = fields.Char(string="Name")
    value = fields.Integer()

    description = fields.Text()

