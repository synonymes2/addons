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

import odoo
from odoo import http,_
from odoo.http import request
from odoo.addons.web.controllers.main import Home, ensure_db

class Home(Home):

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        res = super(Home, self).index(s_action=None, db=None, **kw)
        user = request.env['res.users'].browse([request.session.uid])
        if user and user.has_group("point_of_sale.group_pos_user"):
            if user.default_pos:
                return request.render('web.webclient_custom', {'user':user})
        return res

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        res = super(Home, self).web_client(s_action, **kw)
        user = request.env['res.users'].browse([request.session.uid])
        if user and user.has_group("point_of_sale.group_pos_user"):
            if user.default_pos:
                return request.render('web.webclient_custom', {'user':user})
        return res

    @http.route()
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if kw.get('pos_error'):
            values['error']= _("Another user is already using the POS")
            return request.render('web.login', values)
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                users = request.env['res.users'].browse([uid])
                if users and users.has_group("point_of_sale.group_pos_user"):
                    if users.default_pos:
                        pos_session = request.env['pos.session'].sudo().search(
                            [('config_id', '=', users.default_pos.id), ('state', '=', 'opened')])
                        if pos_session and pos_session.user_id.id == users.id:
                            return http.redirect_with_hash('/pos/web')
                        elif pos_session and pos_session.user_id.id != users.id:
                            return http.redirect_with_hash('/web/session/logout/?redirect=/web/login?pos_error=True')
                        else:
                            session_id = users.default_pos.open_session_cb()
                            pos_session = request.env['pos.session'].sudo().search(
                                [('config_id', '=', users.default_pos.id), ('state', '=', 'opening_control')])
                            if users.default_pos.cash_control:
                                pos_session.write({'opening_balance': True})
                            session_open = pos_session.action_pos_session_open()
                            return http.redirect_with_hash('/pos/web')
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                    return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('web.login', values)
    
#     @http.route('/web/login', type='http', auth="none", sitemap=False)
#     def web_login(self, redirect=None, **kw):
#         res = super(Home, self).web_login(redirect, **kw)
#         if request.params['login_success']:
#             uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
#             users = request.env['res.users'].browse([uid])
#             if users and users.has_group("point_of_sale.group_pos_manager"):
#                 return res
#             elif users and users.has_group("point_of_sale.group_pos_user"):
#                 if users.default_pos:
#                     pos_session = request.env['pos.session'].sudo().search(
#                         [('config_id', '=', users.default_pos.id), ('state', '=', 'opened')])
#                     if pos_session and pos_session.user_id.id == users.id:
#                         return http.redirect_with_hash('/pos/web')
#                     elif pos_session and pos_session.user_id.id != users.id:
#                         print "\n\n Another user is already using the POS >>>> ",res.qcontext
#                          
#                     else:
#                         session_id = users.default_pos.open_session_cb()
#                         pos_session = request.env['pos.session'].sudo().search(
#                             [('config_id', '=', users.default_pos.id), ('state', '=', 'opening_control')])
#                         if users.default_pos.cash_control:
#                             pos_session.write({'opening_balance': True})
#                         session_open = pos_session.action_pos_session_open()
#                         return http.redirect_with_hash('/pos/web')
#                 else:
#                     return res
#             else:
#                 return res
#         else:
#             return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: