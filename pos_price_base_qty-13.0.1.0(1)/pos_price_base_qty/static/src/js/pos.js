odoo.define('pos_price_base_qty', function (require) {
"use strict";

var models = require('point_of_sale.models');
var chrome = require('point_of_sale.chrome');
var core = require('web.core');
var PosPopWidget = require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var gui = require('point_of_sale.gui');
var screens = require('point_of_sale.screens');
var _t = core._t;


    var EnterProductPriceWidget = PosPopWidget.extend({
        template: 'EnterProductPriceWidget',

        renderElement: function(){
            var self = this;
            this._super();
            this.$(".product_price_button").click(function(){
                var price = $(".product_price").val();
                var line = self.pos.get_order().get_selected_orderline();
                if(line){
                    var unit_price = line.get_unit_price();
                    var qty = price/unit_price;
                    line.set_quantity(qty);
                }
                self.gui.show_screen('products');
            });
        },
        show: function(options){
            var self = this;
            this.options = options || {};
            this._super(options); 
            this.renderElement();
        },
    });

    gui.define_popup({
        'name': 'enter-product-price-widget', 
        'widget': EnterProductPriceWidget,
    });
    var ProductPriceQtyButton = screens.ActionButtonWidget.extend({
        template: 'ProductPriceQtyButton',
        button_click: function(){
            var self = this;
            var line = this.pos.get_order().get_selected_orderline();
            if(line){
                var product = line.get_product();
                self.gui.show_popup('enter-product-price-widget',{product:product});
            }
        },
    });

    screens.define_action_button({
        'name': 'ProductPriceQtyButton',
        'widget': ProductPriceQtyButton,
        'condition': function(){
            return this.pos.config.allow_price_base_qty;
        },
    });
});

