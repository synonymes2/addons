# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Tax on Base Amount",
  "summary"              :  "This module for Tax on Base Amount in POS session.",
  "category"             :  "Point of sale",
  "version"              :  "1.1",
  "author"               :  "Perkup Pvt. Ltd.",
  "depends"              :  ['point_of_sale'],
  
  "data"                 :  [
                             'views/pos_tax_inherit_view.xml',
                             'views/template.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  49,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
