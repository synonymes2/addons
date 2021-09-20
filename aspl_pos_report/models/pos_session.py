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

import logging
from odoo import fields, models, api, SUPERUSER_ID, _, registry
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from datetime import datetime, date, timedelta
from itertools import groupby
import base64
from odoo import SUPERUSER_ID
import threading

_logger = logging.getLogger(__name__)

class pos_session(models.Model):
    _inherit = "pos.session"

    @api.multi
    def action_pos_session_close(self):
        users_email_lst = []
        result = super(pos_session, self).action_pos_session_close()
        self.run_scheduler()
        return result

    @api.model
    def run_scheduler(self):
        threaded_calculation = threading.Thread(target=self.inventory_valuation_by_category, args=())
        threaded_calculation.start()

    @api.multi
    def inventory_valuation_by_category(self):
        with api.Environment.manage():
            new_cr = registry(self._cr.dbname).cursor()
            self = self.with_env(self.env(cr=new_cr))
            scheduler_cron = self.sudo().env.ref('aspl_pos_report.z_report_email_cron')
            result = self.send_email_z_report()
            return result

    def send_email_z_report(self):
        users = self.env['res.users'].search([])
        for user in users:
            if user.send_daily_report:
                if self.config_id.id in user.allow_pos.ids:
                    if user.email:
                        datas = {
                            'ids': self.ids,
                            'model': self._name,
                            'form': self.read()[0]
                        }
                        pdf_data = self.env['report'].get_pdf(self.ids, 'aspl_pos_report.pos_sales_report_pdf_template', data=datas)
                        if pdf_data:
                            pdfvals = {
                                'name': 'Z Report',
                                'db_datas': base64.b64encode(pdf_data),
                                'datas': base64.b64encode(pdf_data),
                                'datas_fname': 'Z Report.pdf',
                                'res_model': 'pos.session',
                                'res_id': self.id,
                                'type': 'binary'
                            }
                            pdf_create = self.env['ir.attachment'].create(pdfvals)
                            mail_obj = self.env['mail.mail']
                            body_html = """<p>Dear %s,</p>
                                <p>
                                    The sale report for %s from %s to %s is attached.
                                </p>
                                <p>Thank you</p>
                                """ % (user.name or '', self.env.user.company_id.name, self.start_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            values = {
                                'subject': 'Z-Report',
                                'body_html': body_html,
                                'email_to': user.email,
                                'email_from': self.env['res.users'].browse(SUPERUSER_ID).email or 'admin@yourcompany.example.com',
                                'attachment_ids': [(6, 0, [pdf_create.id])]
                            }
                            msg_id = mail_obj.create(values)
                            if msg_id:
                                msg_id.send()

    @api.multi
    def get_proxy_ip(self):
        proxy_id = self.env['res.users'].browse([self._uid]).company_id.report_ip_address
        return {'ip': proxy_id or False}

    @api.multi
    def get_user(self):
        if self._uid == SUPERUSER_ID:
            return True
    @api.multi
    def get_gross_total(self):
        gross_total = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    gross_total += line.qty * (line.price_unit - line.product_id.standard_price)
        return gross_total

    @api.multi
    def get_product_cate_total(self):
        balance_end_real = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    balance_end_real += (line.qty * line.price_unit)
        return balance_end_real

    @api.multi
    def get_net_gross_total(self):
        net_gross_profit = 0.0
        if self:
            net_gross_profit = self.get_gross_total() - self.get_total_tax()
        return net_gross_profit

    @api.multi
    def get_product_name(self, category_id):
        if category_id:
            category_name = self.env['pos.category'].browse([category_id]).name
            return category_name

    @api.multi
    def get_payments(self):
        if self:
            statement_line_obj = self.env["account.bank.statement.line"]
            pos_order_obj = self.env["pos.order"]
            company_id = self.env['res.users'].browse([self._uid]).company_id.id
            pos_ids = pos_order_obj.search([('state','in',['paid','invoiced','done']),
                                            ('company_id', '=', company_id),('session_id','=',self.id)])
            data={}
            if pos_ids:
                pos_ids = [pos.id for pos in pos_ids]
                st_line_ids = statement_line_obj.search([('pos_statement_id', 'in', pos_ids)])
                if st_line_ids:
                    a_l=[]
                    for r in st_line_ids:
                        a_l.append(r['id'])
                    self._cr.execute("select aj.name,sum(amount) from account_bank_statement_line as absl,account_bank_statement as abs,account_journal as aj " \
                                    "where absl.statement_id = abs.id and abs.journal_id = aj.id  and absl.id IN %s " \
                                    "group by aj.name ",(tuple(a_l),))

                    data = self._cr.dictfetchall()
                    return data
            else:
                return {}

    @api.multi
    def get_product_category(self):
        product_list = []
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    flag = False
                    product_dict = {}
                    for lst in product_list:
                        if line.product_id.pos_categ_id:
                            if lst.get('pos_categ_id') == line.product_id.pos_categ_id.id:
                                lst['price'] = lst['price'] + (line.qty * line.price_unit)
                                flag = True
                        else:
                            if lst.get('pos_categ_id') == '':
                                lst['price'] = lst['price'] + (line.qty * line.price_unit)
                                flag = True
                    if not flag:
                        product_dict.update({
                                    'pos_categ_id': line.product_id.pos_categ_id and line.product_id.pos_categ_id.id or '',
                                    'price': (line.qty * line.price_unit)
                                })
                        product_list.append(product_dict)
        return product_list

    @api.multi
    def get_journal_amount(self):
        journal_list = []
        if self and self.statement_ids:
            for statement in self.statement_ids:
                journal_dict = {}
                journal_dict.update({'journal_id': statement.journal_id and statement.journal_id.name or '',
                                     'ending_bal': statement.balance_end_real or 0.0})
                journal_list.append(journal_dict)
        return journal_list

    @api.multi
    def get_total_closing(self):
        if self:
            return self.cash_register_balance_end_real

    @api.multi
    def get_total_sales(self):
        total_price = 0.0
        if self:
            for order in self.order_ids:
#                 for line in order.lines:
#                     discount = ((line.qty * line.price_unit) * line.discount) / 100
#                     total_price += (line.price_unit - discount)
#                 total_price += sum([(line.qty * line.price_unit) for line in order.lines])
                total_price += (order.amount_total)
        return total_price

    @api.multi
    def get_total_tax(self):
        if self:
            total_tax = 0.0
            pos_order_obj = self.env['pos.order']
            total_tax += sum([order.amount_tax for order in pos_order_obj.search([('session_id', '=', self.id)])])
        return total_tax

    @api.multi
    def get_vat_tax(self):
        taxes_info = []
        if self:
            tax_list = []
            tax_list = [tax.id for order in self.order_ids for line in order.lines.filtered(lambda line: line.tax_ids_after_fiscal_position) for tax in line.tax_ids_after_fiscal_position]
            tax_list = list(set(tax_list))
            for tax in self.env['account.tax'].browse(tax_list):
                total_tax = 0.00
                net_total = 0.00
                for line in self.env['pos.order.line'].search([('order_id', 'in', [order.id for order in self.order_ids])]).filtered(lambda line: tax in line.tax_ids_after_fiscal_position ):
                    total_tax += line.price_subtotal * tax.amount / 100
                    net_total += line.price_subtotal
                taxes_info.append({
                    'tax_name': tax.name,
                    'tax_total': "%.2f" % total_tax,
                    'tax_per': tax.amount,
                    'net_total': net_total,
                    'gross_tax': total_tax + net_total
                })
        return taxes_info

    @api.multi
    def get_total_discount(self):
        total_discount = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                total_discount += sum([((line.qty * line.price_unit) * line.discount) / 100 for line in order.lines])
        return total_discount

    @api.multi
    def get_total_first(self):
        total = 0.0
        if self:
            total = (self.get_total_sales() + self.get_total_tax())\
                - (abs(self.get_total_discount()))
        return total

    @api.multi
    def get_session_date(self, date_time):
        if date_time:
            if self._context and self._context.get('tz'):
                tz = timezone(self._context.get('tz'))
            else:
                tz = pytz.utc
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            if sign == '+':
                date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) + \
                                                    timedelta(hours=hour_tz, minutes=min_tz)
            else:
                date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) - \
                                                    timedelta(hours=hour_tz, minutes=min_tz)
            return date_time.strftime('%d/%m/%Y %I:%M:%S %p')

    @api.multi
    def get_session_time(self, date_time):
        if date_time:
            if self._context and self._context.get('tz'):
                tz = timezone(self._context.get('tz'))
            else:
                tz = pytz.utc
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            if sign == '+':
                date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) + \
                                                    timedelta(hours=hour_tz, minutes=min_tz)
            else:
                date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) - \
                                                    timedelta(hours=hour_tz, minutes=min_tz)
            return date_time.strftime('%I:%M:%S %p')

    @api.multi
    def get_current_date(self):
        if self._context and self._context.get('tz'):
            tz = self._context['tz']
            tz = timezone(tz)
        else:
            tz = pytz.utc
        if tz:
#             tz = timezone(tz)
            c_time = datetime.now(tz)
            return c_time.strftime('%d/%m/%Y')
        else:
            return date.today().strftime('%d/%m/%Y')

    @api.multi
    def get_current_time(self):
        if self._context and self._context.get('tz'):
            tz = self._context['tz']
            tz = timezone(tz)
        else:
            tz = pytz.utc
        if tz:
#             tz = timezone(tz)
            c_time = datetime.now(tz)
            return c_time.strftime('%I:%M %p')
        else:
            return datetime.now().strftime('%I:%M:%S %p')

    @api.multi
    def get_company_data_x(self):
        return self.user_id.company_id

    @api.multi
    def get_pos_name(self):
        if self and self.config_id:
            return self.config_id.name

    @api.multi
    def get_current_date_x(self):
        if self._context and self._context.get('tz'):
            tz = self._context['tz']
            tz = timezone(tz)
        else:
            tz = pytz.utc
        if tz:
#             tz = timezone(tz)
            c_time = datetime.now(tz)
            return c_time.strftime('%d/%m/%Y')
        else:
            return date.today().strftime('%d/%m/%Y')
    
    @api.multi
    def get_session_date_x(self, date_time):
        if date_time:
            if self._context and self._context.get('tz'):
                tz = self._context['tz']
                tz = timezone(tz)
            else:
                tz = pytz.utc
            if tz:
#                 tz = timezone(tz)
                c_time = datetime.now(tz)
                hour_tz = int(str(c_time)[-5:][:2])
                min_tz = int(str(c_time)[-5:][3:])
                sign = str(c_time)[-6][:1]
                if sign == '+':
                    date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) + \
                                                        timedelta(hours=hour_tz, minutes=min_tz)
                else:
                    date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) - \
                                                        timedelta(hours=hour_tz, minutes=min_tz)
            else:
                date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT)
            return date_time.strftime('%d/%m/%Y')

    @api.multi
    def get_current_time_x(self):
        if self._context and self._context.get('tz'):
            tz = self._context['tz']
            tz = timezone(tz)
        else:
            tz = pytz.utc
        if tz:
#             tz = timezone(tz)
            c_time = datetime.now(tz)
            return c_time.strftime('%I:%M %p')
        else:
            return datetime.now().strftime('%I:%M:%S %p')
    
    @api.multi
    def get_session_time_x(self, date_time):
        if date_time:
            if self._context and self._context.get('tz'):
                tz = self._context['tz']
                tz = timezone(tz)
            else:
                tz = pytz.utc
            if tz:
#                 tz = timezone(tz)
                c_time = datetime.now(tz)
                hour_tz = int(str(c_time)[-5:][:2])
                min_tz = int(str(c_time)[-5:][3:])
                sign = str(c_time)[-6][:1]
                if sign == '+':
                    date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) + \
                                                        timedelta(hours=hour_tz, minutes=min_tz)
                else:
                    date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT) - \
                                                        timedelta(hours=hour_tz, minutes=min_tz)
            else:
                date_time = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT)
            return date_time.strftime('%I:%M:%S %p')

    @api.multi
    def get_total_sales_x(self):
        total_price = 0.0
        if self:
            for order in self.order_ids:
#                     for line in order.lines:
#                         discount = ((line.qty * line.price_unit) * line.discount) / 100
#                         total_price += (line.price_unit - discount)
                total_price += (order.amount_total)
        return total_price

    @api.multi
    def get_sales_by_category(self):
        record_lst = []
        res = []
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    record = {
                        'categ_name':line.product_id.categ_id.name,
                        'qty':line.qty,
                        'price':line.price_subtotal,
                    }
                    record_lst.append(record)
        if len(record_lst) > 0:
            key = lambda x:x['categ_name']
            for k,v in groupby(sorted(record_lst, key=key), key=key):
                price = qty = 0
                for each in v:
                    price += float(each['price'])
                    qty += float(each['qty'])
                res.append({'categ_name':k, 'price': price, 'qty': qty})
        return res

    @api.multi
    def get_total_returns_x(self):
        pos_order_obj = self.env['pos.order']
        total_return = 0.0
        if self:
            for order in pos_order_obj.search([('session_id', '=', self.id)]):
                if order.amount_total < 0:
                    total_return += abs(order.amount_total)
        return total_return

    @api.multi
    def get_total_tax_x(self):
        total_tax = 0.0
        if self:
            pos_order_obj = self.env['pos.order']
            total_tax += sum([order.amount_tax for order in pos_order_obj.search([('session_id', '=', self.id)])])
        return total_tax

    @api.multi
    def get_total_discount_x(self):
        total_discount = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                total_discount += sum([((line.qty * line.price_unit) * line.discount) / 100 for line in order.lines])
        return total_discount

    @api.multi
    def get_money_in_total(self):
        if self:
            amount = 0
            account_bank_stmt_ids = self.env['account.bank.statement'].search([('pos_session_id','=',self.id)])
            for account_bank_stmt in account_bank_stmt_ids:
                for line in account_bank_stmt.line_ids:
                    if line and line.is_money_in:
                        amount += line.amount
        return amount

    @api.multi
    def get_money_out_total(self):
        if self:
            amount = 0
            account_bank_stmt_ids = self.env['account.bank.statement'].search([('pos_session_id','=',self.id)])
            for account_bank_stmt in account_bank_stmt_ids:
                for line in account_bank_stmt.line_ids:
                    if line and line.is_money_out:
                        amount += line.amount
        return amount

    @api.multi
    def get_money_out_details(self):
        money_out_lst = []
        if self:
            account_bank_stmt_ids = self.env['account.bank.statement'].search([('pos_session_id','=',self.id)])
            for account_bank_stmt in account_bank_stmt_ids:
                for line in account_bank_stmt.line_ids:
                    if line and line.is_money_out:
                        money_out_lst.append({
                            'name': line.name,
                            'amount':line.amount,
                        })
        return money_out_lst

    @api.multi
    def get_money_in_details(self):
        money_in_lst = []
        if self:
            account_bank_stmt_ids = self.env['account.bank.statement'].search([('pos_session_id','=',self.id)])
            for account_bank_stmt in account_bank_stmt_ids:
                for line in account_bank_stmt.line_ids:
                    if line and line.is_money_in:
                        money_in_lst.append({
                            'name': line.name,
                            'amount':line.amount,
                        })
        return money_in_lst

    @api.multi
    def get_discount_details(self):
        newresult = []
        if self and self.order_ids:
            result = {}
            discount_lst = []
            for order in self.order_ids:
                result.update({order.id: []})
                discount_lst = []
                for line in order.lines:
                    if line.discount_id :
                        discount_data = {
                            'discount_id':line.discount_id.id,
                            'discount_name':line.discount_id.name,
                            'discount':line.discount,
                            'order_id': order.id,
                        }
                        discount_lst.append(discount_data)
                result[order.id] = discount_lst
            res = {}
            for key, vals in result.items():
                for each in vals:
                    if each['discount_id'] not in res:
                        res.update({each['discount_id']: {'discount': 0, 'discount_name': each['discount_name'], 'count': {key: key}}})
                    res[each['discount_id']]['discount'] += each['discount']
                    res[each['discount_id']]['count'].update({key: key})
            for key, each in res.items():
                vals = each
                vals.update({'count': len(vals['count'].keys())})
                newresult.append(vals)
        return newresult

    @api.multi
    def get_total_first_x(self):
        global gross_total
        if self:
            gross_total = (self.get_total_sales() + self.get_total_tax()) \
                 + self.get_total_discount()
        return gross_total
    
    @api.multi
    def get_user_x(self):
        if self._uid == SUPERUSER_ID:
            return True

    @api.multi
    def get_gross_total_x(self):
        total_cost = 0.0
        gross_total = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    total_cost += line.qty * line.product_id.standard_price
        gross_total = self.get_total_sales() - \
                    + self.get_total_tax() - total_cost
        return gross_total

    @api.multi
    def get_net_gross_total_x(self):
        net_gross_profit = 0.0
        total_cost = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    total_cost += line.qty * line.product_id.standard_price
            net_gross_profit = self.get_total_sales() - self.get_total_tax() - total_cost
        return net_gross_profit

    @api.multi
    def get_product_cate_total_x(self):
        balance_end_real = 0.0
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    balance_end_real += (line.qty * line.price_unit)
        return balance_end_real

    @api.multi
    def get_product_name_x(self, category_id):
        if category_id:
            category_name = self.env['pos.category'].browse([category_id]).name
            return category_name

    @api.multi
    def get_product_category_x(self):
        product_list = []
        if self and self.order_ids:
            for order in self.order_ids:
                for line in order.lines:
                    flag = False
                    product_dict = {}
                    for lst in product_list:
                        if line.product_id.pos_categ_id:
                            if lst.get('pos_categ_id') == line.product_id.pos_categ_id.id:
                                lst['price'] = lst['price'] + (line.qty * line.price_unit)
#                                 if line.product_id.pos_categ_id.show_in_report:
                                lst['qty'] = lst.get('qty') or 0.0 + line.qty
                                flag = True
                        else:
                            if lst.get('pos_categ_id') == '':
                                lst['price'] = lst['price'] + (line.qty * line.price_unit)
                                lst['qty'] = lst.get('qty') or 0.0 + line.qty
                                flag = True
                    if not flag:
                        if line.product_id.pos_categ_id:
                            product_dict.update({
                                        'pos_categ_id': line.product_id.pos_categ_id and line.product_id.pos_categ_id.id or '',
                                        'price': (line.qty * line.price_unit),
                                        'qty': line.qty
                                    })
                        else:
                            product_dict.update({
                                        'pos_categ_id': line.product_id.pos_categ_id and line.product_id.pos_categ_id.id or '',
                                        'price': (line.qty * line.price_unit),
                                    })
                        product_list.append(product_dict)
        return product_list

    @api.multi
    def count_payment_method_by_id(self, journal_id):
        count = 0
        if self and journal_id:
            pos_order_ids = self.env['pos.order'].search([('session_id','=',self.id)])
            for pos_order in pos_order_ids:
                for statement in pos_order.statement_ids:
                    if statement.journal_id and statement.journal_id.id == journal_id:
                        if statement.journal_id.type == 'cash' and statement.amount > 0:
                            count += 1
                        elif statement.journal_id.type != 'cash':
                            count += 1
        return count

    @api.multi
    def get_percentage_by_payment_method(self, journal_id):
        current_journal_count = 0
        all_journal_count = 0
        pos_order_ids = self.env['pos.order'].search([('session_id','=',self.id)])
        for pos_order in pos_order_ids:
            for statement in pos_order.statement_ids:
                if statement.journal_id and statement.journal_id.id == journal_id:
                        if statement.journal_id.type == 'cash' and statement.amount > 0:
                            current_journal_count += 1
                        elif statement.journal_id.type != 'cash':
                            current_journal_count += 1
                if statement.journal_id.type == 'cash' and statement.amount > 0:
                    all_journal_count += 1
                elif statement.journal_id.type != 'cash':
                    all_journal_count += 1
        percentage = (float(current_journal_count)/float(all_journal_count)) * 100
        return percentage

    @api.multi
    def get_payment_amount_percentage(self, amount):
        st_amount = 0
        pos_order_ids = self.env['pos.order'].search([('session_id','=',self.id)])
        for pos_order in pos_order_ids:
            for statement in pos_order.statement_ids:
                st_amount += statement.amount
        percentage = (float(amount) / float(st_amount)) * 100
        return percentage

    @api.multi
    def get_payments_x(self):
        if self:
            statement_line_obj = self.env["account.bank.statement.line"]
            pos_order_obj = self.env["pos.order"]
            company_id = self.env['res.users'].browse([self._uid]).company_id.id
            pos_ids = pos_order_obj.search([('session_id', '=', self.id),
                                            ('state', 'in', ['paid', 'invoiced', 'done']),
                                            ('user_id', '=', self.user_id.id), ('company_id', '=', company_id)])
            data = {}
            if pos_ids:
                pos_ids = [pos.id for pos in pos_ids]
                st_line_ids = statement_line_obj.search([('pos_statement_id', 'in', pos_ids)])
                if st_line_ids:
                    a_l = []
                    for r in st_line_ids:
                        a_l.append(r['id'])
                    self._cr.execute("select aj.id,aj.name,sum(amount) from account_bank_statement_line as absl,account_bank_statement as abs,account_journal as aj " \
                                    "where absl.statement_id = abs.id and abs.journal_id = aj.id  and absl.id IN %s " \
                                    "group by aj.name, aj.id ", (tuple(a_l),))

                    data = self._cr.dictfetchall()
                    return data
            else:
                return {}

    @api.multi
    def get_order_exclude_return(self):
        order_count = 0
        if self and self.order_ids:
            for order in self.order_ids:
                if order.amount_total > 0:
                    order_count += 1
        return order_count

    @api.multi
    def is_restaurant_installed(self):
        restaurant_module = self.env['ir.module.module'].sudo().search([('name','=', 'pos_restaurant')])
        if restaurant_module and restaurant_module.state == 'installed':
            return True
        return False

    @api.multi
    def is_pos_custom_discounts_installed(self):
        custom_discount_module = self.env['ir.module.module'].sudo().search([('name','=', 'pos_custom_discounts')])
        if custom_discount_module and custom_discount_module.state == 'installed':
            return True
        return False

    @api.multi
    def is_pos_order_cancel_installed(self):
        pos_order_cancel_module = self.env['ir.module.module'].sudo().search([('name','=', 'pos_order_cancel')])
        pos_order_cancel_restaurant_module = self.env['ir.module.module'].search([('name','=', 'pos_order_cancel_restaurant')])
        if pos_order_cancel_module and pos_order_cancel_module.state == 'installed':
            return True
        if pos_order_cancel_restaurant_module and pos_order_cancel_restaurant_module.state == 'installed':
            return True
        return False

    @api.multi
    def get_guest_numbers(self):
        customer_count = 0
        if self and self.order_ids:
            for order in self.order_ids:
                customer_count += order.customer_count
        return customer_count

    @api.multi
    def get_net_sales(self):
        result = (((self.get_total_sales_x() + self.get_total_discount_x() + self.get_total_returns_x()) 
                - self.get_total_discount_x() - self.get_total_returns_x()) - self.get_total_tax_x())
        return result or 1

    @api.multi
    def get_total_orders(self):
        return len(self.order_ids) or 1

    @api.multi
    def get_void_report_data(self):
        order_ids = []
        records_list = []
        if self and self.order_ids:
            for order in self.order_ids:
                order_ids.append(order.id)
        if len(order_ids) > 0:
            cancel_order_line = self.env['pos.order.line.canceled'].search([('order_id','in',order_ids)])
            if cancel_order_line:
                for line in cancel_order_line:
                    records_list.append({
                        'product_name': line.product_id.name,
                        'qty': line.qty,
                        'value': line.price_subtotal_incl
                    })
        return records_list

    @api.multi
    def get_cash_control_info(self):
        tender_list = []
        custom_close_session_module = self.env['ir.module.module'].sudo().search([('name','=', 'aspl_pos_close_session')])
        if custom_close_session_module and custom_close_session_module.state == 'installed':
            if self and self.cashcontrol_ids:
                for each in self.cashcontrol_ids:
                    tender_list.append({
                        'journal_id':each.journal_id,
                        'amount':each.amount,
                        'transaction_subtotal':each.transaction_subtotal,
                        'difference':each.difference
                    })
        if tender_list:
            return tender_list

class res_company(models.Model):
    _inherit = 'res.company'

    report_ip_address = fields.Char(string="Thermal Printer Proxy IP")


class res_users(models.Model):
    _inherit = 'res.users'

    send_daily_report = fields.Boolean("Send Daily Report")
    allow_pos = fields.Many2many('pos.config' ,string="Allow POS")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: