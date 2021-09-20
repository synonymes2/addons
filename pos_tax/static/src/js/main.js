odoo.define('pos_tax.pos_tax', function (require) {
"use strict";
	var models = require('point_of_sale.models');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var pos_model = require('point_of_sale.models');
	var core = require('web.core');
	var _t = core._t;
	var screens = require('point_of_sale.screens');
	var popup_widget = require('point_of_sale.popups');
	var SuperOrder = models.Order;
	var SuperOrderline = pos_model.Orderline;
	var QWeb = core.qweb;
	var utils = require('web.utils');
	var round_di = utils.round_decimals;
	var round_pr = utils.round_precision;
	var PosDB = require('point_of_sale.DB');	
	/*
	models.load_models([{
		model:'pos.custom.discount',
		field: [],
		domain:function(self){
			return [['id','in',self.config.discount_ids]];
		},
		loaded: function(self,result) {
			self.all_discounts = result;
		}

	},
	],
		{
			'before': 'pos.category'
		}
	);*/
	
	pos_model.Orderline = pos_model.Orderline.extend({			
		initialize: function(attr,options){
//			this.custom_discount_reason='';
//			this.new_type='';
	        this.db = new PosDB();                       // a local database used to search trough products and categories & store pending orders			
			SuperOrderline.prototype.initialize.call(this,attr,options);
		},
		
		get_tax: function(){
		    return this.get_all_prices().tax;
		},

		_compute_all: function(tax, base_amount, quantity) {
			if (tax.amount_type === 'fixed') {
				var sign_base_amount = base_amount >= 0 ? 1 : -1;
				return (Math.abs(tax.amount) * sign_base_amount) * quantity;
			}
			if ((tax.amount_type === 'percent' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){
				return base_amount * tax.amount / 100;
			}
			if (tax.amount_type === 'percent' && tax.price_include){
				return base_amount - (base_amount / (1 + tax.amount / 100));
			}
			if (tax.amount_type === 'division' && !tax.price_include) {
				return base_amount / (1 - tax.amount / 100) - base_amount;
			}
			if ((tax.amount_type === 'original_amt' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){				
				return base_amount * tax.amount / 100;
			}
			if (tax.amount_type === 'original_amt' && tax.price_include){
				return base_amount - (base_amount / (1 + tax.amount / 100));
			}
			return false;
		},
	    
		
	    get_all_prices: function(){

			var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
	        var taxtotal = 0;
	        var product =  this.get_product();
	        var taxes_ids = product.taxes_id;
	        var taxes =  this.pos.taxes;
	        var taxdetail = {};
	        var product_taxes = [];
	        _(taxes_ids).each(function(el){
	            product_taxes.push(_.detect(taxes, function(t){
	                return t.id === el;
	            }));
	        });
			if (product_taxes && product_taxes.length) {
				var amt_type = product_taxes[0]['amount_type']			
				if (amt_type){
					
					if (amt_type == 'original_amt'){	
						var price_unit = this.get_unit_price() * 1.0;
						//alert(JSON.stringify(price_unit))		 											
						var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding)
					}		
					else { 	
						var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);						
					}
				}
			}
			else {
				var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);

			}

//			alert(JSON.stringify(all_taxes))					
	        _(all_taxes.taxes).each(function(tax) {
	            taxtotal += tax.amount;
	            taxdetail[tax.id] = tax.amount;
	        })

			if (product_taxes && product_taxes.length && product_taxes[0]['amount_type'] == 'original_amt') {
		    	return {
			            "priceWithTax": (all_taxes.total_included * (1.0 - (this.get_discount() / 100.0))),
			            "priceWithoutTax": (all_taxes.total_excluded * (1.0 - (this.get_discount() / 100.0))),
//			            "priceWithTax": (all_taxes.total_included - this.get_discount()),
//			            "priceWithoutTax": (all_taxes.total_excluded - this.get_discount()),
					    "tax": taxtotal,
					    "taxDetails": taxdetail,
					}
				}
			else
				{
		    	return {
			            "priceWithTax": all_taxes.total_included,
			            "priceWithoutTax": all_taxes.total_excluded,
					    "tax": taxtotal,
					    "taxDetails": taxdetail,
						}
							
				}

				
			//alert(JSON.stringify(all_taxes))		

/*
	        if (this.get_set_type() == 'cash' ) {
				if (product_taxes && product_taxes.length && product_taxes[0]['amount_type'] == 'original_amt') {
				    	return {
				            "priceWithTax": (all_taxes.total_included - this.get_discount()),
				            "priceWithoutTax": (all_taxes.total_excluded - this.get_discount()),
						    "tax": taxtotal,
						    "taxDetails": taxdetail,
						}
					}
				else
					{
				    	return {
				            "priceWithTax": all_taxes.total_included,
				            "priceWithoutTax": all_taxes.total_excluded,
						    "tax": taxtotal,
						    "taxDetails": taxdetail,
						}
							
					}
			}
			else if (this.get_set_type() == 'percent') {
				if (product_taxes && product_taxes.length && product_taxes[0]['amount_type'] == 'original_amt') {
			    	return {
			            "priceWithTax": (all_taxes.total_included * (1.0 - (this.get_discount() / 100.0))),
			            "priceWithoutTax": (all_taxes.total_excluded * (1.0 - (this.get_discount() / 100.0))),
					    "tax": taxtotal,
					    "taxDetails": taxdetail,
						}
					}
				else {					
		      		return {
			      		"priceWithTax": all_taxes.total_included,
				        "priceWithoutTax": all_taxes.total_excluded,
				        "tax": taxtotal,
				        "taxDetails": taxdetail,
		      		}
				}
			}					

			else {
				return {
	          		"priceWithTax": all_taxes.total_included,
		            "priceWithoutTax": all_taxes.total_excluded,
		            "tax": taxtotal,
		            "taxDetails": taxdetail,
         		};
			}*/
	    }, 

	});
	
});
