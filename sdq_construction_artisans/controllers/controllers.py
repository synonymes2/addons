# -*- coding: utf-8 -*-
from odoo import http

# class SdqConstructionArtisans(http.Controller):
#     @http.route('/sdq_construction_artisans/sdq_construction_artisans/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sdq_construction_artisans/sdq_construction_artisans/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sdq_construction_artisans.listing', {
#             'root': '/sdq_construction_artisans/sdq_construction_artisans',
#             'objects': http.request.env['sdq_construction_artisans.sdq_construction_artisans'].search([]),
#         })

#     @http.route('/sdq_construction_artisans/sdq_construction_artisans/objects/<model("sdq_construction_artisans.sdq_construction_artisans"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sdq_construction_artisans.object', {
#             'object': obj
#         })