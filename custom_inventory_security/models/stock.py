from odoo import api, models, SUPERUSER_ID
from lxml import etree
from odoo.osv.orm import setup_modifiers


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(stock_picking, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        inventory_user_grp_id = self.env.ref('custom_inventory_security.group_inventory_receipt_type_user').id
        user_group_ids = self.env['res.users'].browse(self._uid).groups_id.ids
        doc = etree.XML(res['arch'])
        if inventory_user_grp_id in user_group_ids:
            nodes = doc.xpath("//field[@name='partner_id']")
            for node in nodes:
                node.set('readonly', '1')
                setup_modifiers(node, res['fields']['partner_id'])
            nodes = doc.xpath("//field[@name='min_date']")
            for node in nodes:
                node.set('readonly', '1')
                setup_modifiers(node, res['fields']['min_date'])
            nodes = doc.xpath("//field[@name='origin']")
            for node in nodes:
                node.set('readonly', '1')
                setup_modifiers(node, res['fields']['origin'])
            nodes = doc.xpath("//field[@name='move_type']")
            for node in nodes:
                node.set('readonly', '1')
                setup_modifiers(node, res['fields']['move_type'])
            nodes = doc.xpath("//field[@name='picking_type_id']")
            for node in nodes:
                node.set('readonly', '1')
                setup_modifiers(node, res['fields']['picking_type_id'])
            nodes = doc.xpath("//field[@name='priority']")
            for node in nodes:
                node.set('readonly', '1')
                setup_modifiers(node, res['fields']['priority'])
        res['arch'] = etree.tostring(doc)
        return res