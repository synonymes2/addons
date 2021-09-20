from odoo import api, models, SUPERUSER_ID


class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if args is None:
            args = []
        user_id = self.env['res.users'].search([('id', '=', self._uid)])
        if self._uid == SUPERUSER_ID:
            if user_id and user_id.has_group('custom_inventory_security.group_inventory_receipt_type_user'):
                menu_ids = []
                xml_id = self.env['ir.model.data'].get_object_reference('custom_inventory_security', 'main_custom_stock_menu_custom')[1]
                if xml_id:
                    menu_ids.append(xml_id)
                if menu_ids:
                    args += [('id', 'not in', menu_ids)]
#         if self._uid != SUPERUSER_ID and user_id and user_id.has_group('custom_inventory_security.group_inventory_receipt_type_user'):
#             cust_menu_id = self.env['ir.model.data'].get_object_reference('custom_inventory_security', 'main_custom_stock_menu_custom')[1]
#             cust_menu_list = []
#             if cust_menu_id:
#                 cust_menu_list.append(cust_menu_id)
#             if cust_menu_list:
#                 args += [('id', 'in', cust_menu_list)]
        return super(ir_ui_menu, self).search(args, offset, limit, order, count=count)
