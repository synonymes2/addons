# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.addons.account.wizard.pos_box import CashBox

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    is_money_in = fields.Boolean("Is Money In");
    is_money_out = fields.Boolean("Is Money Out");

class CashBoxIn(CashBox):
    _inherit = 'cash.box.in'

    @api.multi
    def _calculate_values_for_statement_line(self, record):
        res = super(CashBoxIn, self)._calculate_values_for_statement_line(record)
        if res:
            res.update({
                'is_money_in':True
            })
        return res

class CashBoxOut(CashBox):
    _inherit = 'cash.box.out'

    @api.multi
    def _calculate_values_for_statement_line(self, record):
        res = super(CashBoxOut, self)._calculate_values_for_statement_line(record)
        if res:
            res.update({
                'is_money_out':True
            })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: