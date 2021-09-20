# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _, time


class sdq_construction_artisans(models.Model):
    _name = 'construction.artisans'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('construction.artisans.sequence') or _('New')
        result = super(sdq_construction_artisans, self).create(vals)
        return result

    name_seq = fields.Char(string='ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))

    name = fields.Char(string="Nom De l'Artisans", track_visibility="always",required=True)
    category = fields.Char(string="Departement", track_visibility="always",required=True)
    projet = fields.Many2one(string="Projet",comodel_name='product.template', track_visibility="always", required=True)

    societe = fields.Char(string="nom de societe", track_visibility="always", required=True)
    date = fields.Date('Date de signature', track_visibility="always", required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    company_id = fields.Many2one(
        'res.company', readonly='True', string='Société',
        default=lambda self: self.env['res.company']._company_default_get())
    notes = fields.Text(string="Déscription")
    signed_contract = fields.Binary(string="Document signé", track_visibility="always")
    order_line = fields.One2many('construction.artisans.order.lines', 'order_id', string='Renting details', copy=True)
    # order_id = fields.Many2one('product.template', string='Order Reference', index=True)


class constructionArtisanAdvances(models.Model):
    _name = 'construction.artisans.order.lines'
    artisan_name = fields.Text(string="Nom De l'Artisan")
    date = fields.Date('Date de signature', track_visibility="always", required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    avance = fields.Float(string="Motif De L'Avance ")
    motif = fields.Text(string="Motif")
    total_amount = fields.Float(string="Montant")
    order_id = fields.Many2one('construction.artisans.order.lines', string='Order Reference', index=True)

