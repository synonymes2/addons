# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from mock import DEFAULT
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class FinancingAgreement(models.Model):
    _inherit = "financing.agreement"
    
    invoice_id1 = fields.Many2one('account.invoice', 'Invoice Number')
    
    @api.model
    def default_get(self, fields):
        res = super(FinancingAgreement, self).default_get(fields)
        invoice_obj = self.env['account.invoice'].browse(self._context.get('active_ids'))
        if invoice_obj:
            medical_search = self.env['medical.patient'].search([('name', '=', invoice_obj.partner_id.id)])
            res['name'] = medical_search.id
            res['total_amount_to_be_financed'] = invoice_obj.residual
            res['date_of_service'] = invoice_obj.date_invoice
            res['type_of_service'] = ''
            for inv in invoice_obj.invoice_line_ids:
               res['type_of_service'] += inv.product_id.name + ','
            res['invoice_id1'] = invoice_obj.id
            return res
        else:
            return res
    
    @api.model
    def create(self, vals):
        res = super(FinancingAgreement, self).create(vals)
        active_ids = self._context.get('active_ids')
        if active_ids:
            inv_brw = self.env['account.invoice'].browse(active_ids)
            ret = inv_brw.write({'finance_id': res.id})
        return res
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    finance_id = fields.Many2one('financing.agreement', 'Financing Agreement')
    
    @api.multi
    def financial_agreement_action_inherit1(self):
        finance_id = self.finance_id
        if finance_id:
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'financing.agreement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': finance_id.id,
                    'views': [(False, 'form')],
                    }
        else:
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'financing.agreement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(False, 'form')],
                    }