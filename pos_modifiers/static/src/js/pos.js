odoo.define('pos_modifiers.pos_modifiers', function (require) {
"use strict";

var models = require('point_of_sale.models');
var chrome = require('point_of_sale.chrome');
var core = require('web.core');
var PosPopWidget = require('point_of_sale.popups');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var gui = require('point_of_sale.gui');
var Model = require('web.DataModel');
var screens = require('point_of_sale.screens');
var SuperOrder = models.Order;
var SuperOrderline = models.Orderline;
var PosDB = require('point_of_sale.DB');	
var _t = core._t;
var multiprint = require('pos_restaurant.multiprint');

models.load_fields('product.product',['has_modifier','modifiers_id']);

models.load_models([{
    model: 'product.modifiers',
    condition: function(self){ return self.config.allow_modifiers; },
    fields: ['product_id','amount','qty'],
    loaded: function(self,result){
        if(result.length){
            self.wv_modifiers_list = result;
        }
        else{
            self.wv_modifiers_list = [];
        }
    },
    }],{'after': 'product.product'});


    models.Orderline = models.Orderline.extend({			
		initialize: function(attr,options){
			this.modifier_id='';			
	        this.db = new PosDB();                       // a local database used to search trough products and categories & store pending orders			
			SuperOrderline.prototype.initialize.call(this,attr,options);
		},
		export_for_printing: function(){
			var dict = SuperOrderline.prototype.export_for_printing.call(this);
			dict.modifier_id = this.modifier_id;
			return dict;
		},

        set_modifier_id: function(modifier_id){
	        var disc = modifier_id;
	        this.modifier_id = disc;
	        this.trigger('change',this);
	    },
		get_set_modifier_id: function(){
			var self = this;
			return this.modifier_id;
		},
		export_as_JSON: function() {
			var self = this;
			var loaded=SuperOrderline.prototype.export_as_JSON.call(this);
            loaded.modifier_id=self.get_set_modifier_id();
            return loaded  
        },   
    });

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({

    
    build_line_resume: function(){
        var resume = {};
        this.orderlines.each(function(line){
            if (line.mp_skip) {
                return;
            }
            var line_hash = line.get_line_diff_hash();
            var qty  = Number(line.get_quantity());
            //alert(JSON.stringify(qty))            
            var note = line.get_note();
            var product_id = line.get_product().id;
            var modifier_id = line.get_set_modifier_id();
            if (typeof resume[line_hash] === 'undefined') {
                resume[line_hash] = {
                    qty: qty,
                    note: note,
                    product_id: product_id,
                    modifier_id: modifier_id,
                    product_name_wrapped: line.generate_wrapped_product_name(),
                };
            } else {
                resume[line_hash].qty += qty;
            }

        });
        return resume;
    },


	computeChanges: function(categories){
        var current_res = this.build_line_resume();
        var old_res     = this.saved_resume || {};
        var json        = this.export_as_JSON();
        var add = [];
        var rem = [];
        var line_hash
                for ( line_hash in current_res) {
            var curr = current_res[line_hash];
            var old  = old_res[line_hash];

            if (typeof old === 'undefined') {
                add.push({
                    'id':       curr.product_id,
                    'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                    'name_wrapped': curr.product_name_wrapped,
                    'note':     curr.note,
                    'modifier': curr.modifier_id,
                    'qty':      curr.qty,
                });
            } else if (old.qty < curr.qty) {
                add.push({
                    'id':       curr.product_id,
                    'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                    'name_wrapped': curr.product_name_wrapped,
                    'note':     curr.note,
                    'modifier': curr.modifier_id,
                    'qty':      curr.qty - old.qty,
                });
            } else if (old.qty > curr.qty) {
                rem.push({
                    'id':       curr.product_id,
                    'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                    'name_wrapped': curr.product_name_wrapped,
                    'note':     curr.note,
                    'modifier': curr.modifier_id,
                    'qty':      old.qty - curr.qty,
                });
            }
        }

        for (line_hash in old_res) {
            if (typeof current_res[line_hash] === 'undefined') {
                var old = old_res[line_hash];
                rem.push({
                    'id':       old.product_id,
                    'name':     this.pos.db.get_product_by_id(old.product_id).display_name,
                    'name_wrapped': old.product_name_wrapped,
                    'note':     old.note,
                    'modifier': old.modifier_id,
                    'qty':      old.qty, 
                });
            }
        }

        if(categories && categories.length > 0){
            // filter the added and removed orders to only contains
            // products that belong to one of the categories supplied as a parameter

            var self = this;

            var _add = [];
            var _rem = [];
            
            for(var i = 0; i < add.length; i++){
                if(self.pos.db.is_product_in_category(categories,add[i].id)){
                    _add.push(add[i]);
                }
            }
            add = _add;

            for(var i = 0; i < rem.length; i++){
                if(self.pos.db.is_product_in_category(categories,rem[i].id)){
                    _rem.push(rem[i]);
                }
            }
            rem = _rem;
        }

        var d = new Date();
        var hours   = '' + d.getHours();
            hours   = hours.length < 2 ? ('0' + hours) : hours;
        var minutes = '' + d.getMinutes();
            minutes = minutes.length < 2 ? ('0' + minutes) : minutes;

        return {
            'new': add,
            'cancelled': rem,
            'table': json.table || false,
            'floor': json.floor || false,
            'name': json.name  || 'unknown order',
            'time': {
                'hours':   hours,
                'minutes': minutes,
            },
        };
        
    },

});

/*
var _super_order = models.Order.prototype;
models.Order = models.Order.extend({

    build_line_resume: function(){
        var resume = {};
        this.orderlines.each(function(line){
            if (line.mp_skip) {
                return;
            }
            var line_hash = line.get_line_diff_hash();
            var qty  = Number(line.get_quantity());
            var note = line.get_note();
            var product_id = line.get_product().id;
            var modifier_id = line.get_set_modifier_id();                        
            if (typeof resume[line_hash] === 'undefined') {
                resume[line_hash] = {
                    qty: qty,
                    note: note,
                    product_id: product_id,
                    product_name_wrapped: line.generate_wrapped_product_name(),
            	    modifier_id = modifier_id,                        			
                };
            } else {
                resume[line_hash].qty += qty;
            }

        });
        return resume;
    },

    computeChanges: function(categories){
        var current_res = this.build_line_resume();
        var old_res     = this.saved_resume || {};
        var json        = this.export_as_JSON();
        var add = [];
        var rem = [];
        var line_hash
                for ( line_hash in current_res) {
            var curr = current_res[line_hash];
            var old  = old_res[line_hash];

            if (typeof old === 'undefined') {
                add.push({
                    'id':       curr.product_id,
                    'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                    'name_wrapped': curr.product_name_wrapped,
                    'note':     curr.note,
                    'qty':      curr.qty,
                    'modifier': curr.modifier_id,                    
                });
            } else if (old.qty < curr.qty) {
                add.push({
                    'id':       curr.product_id,
                    'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                    'name_wrapped': curr.product_name_wrapped,
                    'note':     curr.note,
                    'qty':      curr.qty - old.qty,
                    'modifier': curr.modifier_id,                    
                });
            } else if (old.qty > curr.qty) {
                rem.push({
                    'id':       curr.product_id,
                    'name':     this.pos.db.get_product_by_id(curr.product_id).display_name,
                    'name_wrapped': curr.product_name_wrapped,
                    'note':     curr.note,
                    'qty':      old.qty - curr.qty,
                    'modifier': curr.modifier_id,                    
                });
            }
        }

        for (line_hash in old_res) {
            if (typeof current_res[line_hash] === 'undefined') {
                var old = old_res[line_hash];
                rem.push({
                    'id':       old.product_id,
                    'name':     this.pos.db.get_product_by_id(old.product_id).display_name,
                    'name_wrapped': old.product_name_wrapped,
                    'note':     old.note,
                    'qty':      old.qty, 
                    'modifier': old.modifier_id,                    
                });
            }
        }

        if(categories && categories.length > 0){
            // filter the added and removed orders to only contains
            // products that belong to one of the categories supplied as a parameter

            var self = this;

            var _add = [];
            var _rem = [];
            
            for(var i = 0; i < add.length; i++){
                if(self.pos.db.is_product_in_category(categories,add[i].id)){
                    _add.push(add[i]);
                }
            }
            add = _add;

            for(var i = 0; i < rem.length; i++){
                if(self.pos.db.is_product_in_category(categories,rem[i].id)){
                    _rem.push(rem[i]);
                }
            }
            rem = _rem;
        }

        var d = new Date();
        var hours   = '' + d.getHours();
            hours   = hours.length < 2 ? ('0' + hours) : hours;
        var minutes = '' + d.getMinutes();
            minutes = minutes.length < 2 ? ('0' + minutes) : minutes;

        return {
            'new': add,
            'cancelled': rem,
            'table': json.table || false,
            'floor': json.floor || false,
            'name': json.name  || 'unknown order',
            'time': {
                'hours':   hours,
                'minutes': minutes,
            },
        };
        
    },


});
*/
    var ModifiersWidget = PosPopWidget.extend({
        template: 'ModifiersWidget',

        renderElement: function(){
            var self = this;
            var order = this.pos.get_order();
            var flag = false;
            this._super();
            this.$(".add_modifiers").click(function(){
                var product_list = $(".wv_product");
                $(".wv_product").each(function() {
                    if($(this).find("input[type='checkbox']:checked").val() == 'on'){
                        var product_id = $(this).data('product-id');
                        var amount = $(this).data('product-amount');
                        var qty = $(this).data('product-qty');
                        var product = self.pos.db.get_product_by_id(product_id);

			console.log("There is Product ID "+product_id);
			console.log("There is Product "+product);
			var mod = "product modifier id "+product_id //changes1
			console.log(JSON.stringify(product));
			var id_of_base = $('.base_product').data('product-id');
			var base_of_product = self.pos.db.get_product_by_id(id_of_base);
			console.log(JSON.stringify(base_of_product));
            var name_of_base = "tester "+base_of_product.display_name;
            if (flag == false) {
            //alert(JSON.stringify(product))
            //alert(qty)
                self.pos.get_order().add_product(self.pos.db.get_product_by_id(id_of_base));
            }
            flag = true;

           //console.log("Name of BASE PRODUCT is "+base_of_product.display_name);
            
                        self.pos.get_order().add_product(product,{price:amount, quantity:qty, mod:name_of_base});
                        //self.pos.get_order().get_selected_orderline().set_modifier_id(product['id'].display_name);
                      // console.log('This is a product iddd'+product['id']);
                      
                    
                      self.pos.get_order().get_selected_orderline().set_modifier_id(product['display_name']);
                    
                       // self.pos.get_order().get_selected_orderline().set_modifier_id(product['display_name']);
                      //  alert(self.pos.get_order().get_selected_orderline().get_set_modifier_id())
                        //alert(JSON.stringify(product['id']))
                        //self.pos.get_order().add_product(product,{price:amount, quantity:qty});
                    }
                });
                if (flag == false) {
                var p_id = $('.base_product').data('product-id');
			    
               if(p_id){
                    self.pos.get_order().add_product(self.pos.db.get_product_by_id(p_id));
                    //alert(p_id)
               }}
                self.gui.show_screen('products');
            });
            //alert(JSON.stringify(self.pos.get_order()))			
        },
        show: function(options){
            var self = this;
            this.options = options || {};
            var modifiers_list = [];
            var wv_modifiers_list = this.pos.wv_modifiers_list;
            var modifiers_ids = options.product.modifiers_id;
	    
	 
            for(var i=0;i<wv_modifiers_list.length;i++){
                if(modifiers_ids.indexOf(wv_modifiers_list[i].id)>=0){
                    modifiers_list.push(wv_modifiers_list[i]);
		    
                }
            }
	    
	   /* 
	    // Mustafa New Changes Start
		
	    console.log("THis is A stack "+JSON.stringify(modifiers_list.pop())); // Just to check
	    
	    var m_list =[];
	    var c_json={}
	    for(var a=0;a<wv_modifiers_list.length;a++)
	    {
              var modifier_id= wv_modifiers_list[a].id;
	      var id_of_base = $('.base_product').data('modifier_id');
	      var base_of_product = self.pos.db.get_product_by_id(id_of_base);
	      console.log('BASE of product name is '+base_of_product);
	      var n_amount=wv_modifiers_list[a].amount;
	      var n_quantity=wv_modifiers_list[a].qty;
	      var n_id = wv_modifiers_list[a].id;
	      //var n_product_id[]=wv_modifiers_list[a].product_id;
	      
	      var val_json={"amount":n_amount,"quantity":n_quantity,"id":n_id,"name_product":base_of_product}
              m_list.push(val_json);
              

		}
	     console.log("Below is your new changes");
	     console.log(m_list.pop());

		
	    // Mustafa New Changes End
		*/
		
            options.modifiers_list = modifiers_list;
            this._super(options); 
            this.renderElement();
        },
    });

    gui.define_popup({
        'name': 'modifiers-widget', 
        'widget': ModifiersWidget,
    });

    screens.ProductScreenWidget.include({
        click_product: function(product) {
           if(product.to_weight && this.pos.config.iface_electronic_scale){
               this.gui.show_screen('scale',{product: product});
           }else{
                if(this.pos.config.allow_modifiers && product.has_modifier){
                    this.gui.show_popup('modifiers-widget',{'product':product});
                }
                else{
                    this.pos.get_order().add_product(product);
                }
            }
        },

    });
});

