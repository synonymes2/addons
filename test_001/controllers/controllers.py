# -*- coding: utf-8 -*-
from odoo import http

# class Test001(http.Controller):
#     @http.route('/test_001/test_001/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_001/test_001/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_001.listing', {
#             'root': '/test_001/test_001',
#             'objects': http.request.env['test_001.test_001'].search([]),
#         })

#     @http.route('/test_001/test_001/objects/<model("test_001.test_001"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_001.object', {
#             'object': obj
#         })