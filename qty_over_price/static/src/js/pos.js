odoo.define('qty_over_price', function (require) {
    var screens = require("point_of_sale.screens");
    var core = require("web.core");
    var models = require("point_of_sale.models");
    /*var gui = require("point_of_sale.gui");
    var models = require("point_of_sale.models");
    var PopupWidget = require("point_of_sale.popups");
    var rpc = require('web.rpc');
    var _t = core._t;
    */
    screens.OrderWidget.include({
        set_value: function(val) {
          var order = this.pos.get_order();
          /* Old logic */
          /*order.get_selected_orderline().set_quantity(val);*/


          /* New LOGIC */
          if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
               if( mode === 'quantity'){
                price = this.numpad_state.attributes.buffer
                var line = this.pos.get_order().get_selected_orderline();


                if(line){
                    var unit_price = line.get_unit_price();
                    if(price===''||price===0 ){
                        /* To delete this order */
                        line.set_quantity('remove');
                    }else{
                        /* TO SET QUANTITY */
                        var qty = price/unit_price;
                        line.set_quantity(qty);
                    }
                }

            /* Orignal method */
              }else if( mode === 'discount'){
                  order.get_selected_orderline().set_discount(val);
              }else if( mode === 'price'){
                  var selected_orderline = order.get_selected_orderline();
                  selected_orderline.price_manually_set = true;
                  selected_orderline.set_unit_price(val);
              }
                if (this.pos.config.iface_customer_facing_display) {
                      this.pos.send_current_order_to_customer_facing_display();
                };
          };
        },
       });//screens
  


});