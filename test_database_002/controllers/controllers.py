# -*- coding: utf-8 -*-
from odoo import http

# class TestDatabase002(http.Controller):
#     @http.route('/test_database_002/test_database_002/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_database_002/test_database_002/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_database_002.listing', {
#             'root': '/test_database_002/test_database_002',
#             'objects': http.request.env['test_database_002.test_database_002'].search([]),
#         })

#     @http.route('/test_database_002/test_database_002/objects/<model("test_database_002.test_database_002"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_database_002.object', {
#             'object': obj
#         })