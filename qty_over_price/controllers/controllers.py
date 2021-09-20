# -*- coding: utf-8 -*-
from odoo import http

# class QtyOverPrice(http.Controller):
#     @http.route('/qty_over_price/qty_over_price/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/qty_over_price/qty_over_price/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('qty_over_price.listing', {
#             'root': '/qty_over_price/qty_over_price',
#             'objects': http.request.env['qty_over_price.qty_over_price'].search([]),
#         })

#     @http.route('/qty_over_price/qty_over_price/objects/<model("qty_over_price.qty_over_price"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('qty_over_price.object', {
#             'object': obj
#         })