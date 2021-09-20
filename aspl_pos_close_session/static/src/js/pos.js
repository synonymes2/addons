odoo.define('aspl_pos_close_session.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var chrome = require('point_of_sale.chrome');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var _t = core._t;
    var QWeb = core.qweb;
    var framework = require('web.framework');

    models.load_fields("pos.session", ['opening_balance']);
    models.load_fields("res.users", ['default_pos']);

    chrome.HeaderButtonWidget.include({
        renderElement: function(){
            var self = this;
            this._super();
            if(this.action){
                this.$el.click(function(){
                    self.gui.show_popup('confirm_close_session_wizard');
                });
            }
        },
    });

    chrome.Chrome.include({
          build_widgets:function(){
                var self = this;
                this._super(arguments);
                if(self.pos.pos_session.opening_balance){
                    self.gui.show_screen('openingbalancescreen');
                } else{
                    self.gui.show_screen('products');
                }
          },
     });

    var ConfirmCloseSessionPopupWizard = PopupWidget.extend({
        template: 'ConfirmCloseSessionPopupWizard',
        show: function(options){
            options = options || {};
            this._super(options);
            this.statement_id = options.statement_id;
            var self = this;
        },
        click_confirm: function(){
            var self = this;
            var difference = 0;
            new Model("pos.session").call("search_read", [[['id', '=', self.pos.pos_session.id]], ['cash_register_difference'], 0, 1, 'id desc', {}],{}, {'async': false})
            .then(function(session){
            	if(session && session[0]){
            		difference = session[0].cash_register_difference;
            	}
            });
            self.gui.show_popup('tender_popup_wizard',{'difference':difference});
        },
    });
    gui.define_popup({name:'confirm_close_session_wizard', widget: ConfirmCloseSessionPopupWizard});

    var TenderPopupWizard = PopupWidget.extend({
        template: 'TenderPopupWizard',
        show: function(options){
            options = options || {};
            this.difference = options.difference || 0;
            this._super(options);
            var self = this;
            this.renderElement();
            $('#tender td:last-child input').each(function() {
                $(this).focus();
                return false;
            });
            $('table#tender input').keypress(function(event) {
        	    if ((event.which != 46 || $(this).val().indexOf('.') != -1) && (event.which < 48 || event.which > 57)) {
        	        event.preventDefault();
        	    }
        	});

        },
        click_confirm: function(){
            var self = this;
            var tender_list = [];
            $('#tender tr').each(function() {
            	var journal_id = Number($(this).attr('journal-id'));
            	var amount = Number($(this).find('td:last-child input').val() || 0.00);
            	if(journal_id){
            		tender_list.push({
                		'journal_id':journal_id,
                		'amount':amount,
                		'pos_session_id':self.pos.pos_session.id,
                	});
            	}
            });
            if(tender_list.length > 0){
            	new Model('pos.session').call('cash_control_line',
                [self.pos.pos_session.id,tender_list], {}, { async: false })
                .then(function(res){
                    if(res){
                    	new Model('pos.session').call('custom_close_pos_session',
                        [self.pos.pos_session.id], {}, { async: false })
                        .then(function(result){
                            if(result){
                            	var cashier = self.pos.get_cashier() || self.pos.user;
                            	if(cashier && cashier.role != 'manager'){
                            		if(cashier.default_pos && cashier.default_pos[0]){
                            			framework.redirect('/web/session/logout');
                            		}else{
                            			self.pos.gui.close();
                            		}
                            	}else{
                            		self.pos.gui.close();
                            	}
                            }
                        }).fail(function (type, error){
                            if(error.code === 200 ){    // Business Logic Error, not a connection problem
                                self.gui.show_popup('error-traceback',{
                                     'title': error.data.message,
                                     'body':  error.data.debug
                                });
                             }
                         });
                    }else{
                    	alert("Can't close session, Please try again!");
                    }
                }).fail(function (type, error){
                    if(error.code === 200 ){    // Business Logic Error, not a connection problem
                       self.gui.show_popup('error-traceback',{
                            'title': error.data.message,
                            'body':  error.data.debug
                       });
                    }
                });
            }
        },
    });
    gui.define_popup({name:'tender_popup_wizard', widget: TenderPopupWizard});

    var OpeningBalanceScreenWidget = screens.ScreenWidget.extend({
        template: 'OpeningBalanceScreenWidget',
        init: function(parent, options){
            var self = this;
            this._super(parent, options);
        },
        show: function() {
        	this._super();
        	var self = this;
        	this.renderElement();
        	$('#skip').click(function(){
                self.gui.show_screen('products');
                new Model('pos.session').call('close_open_balance',
                [self.pos.pos_session.id], {}, { async: false })
                .then(function(data){
                });
        	});
        	$(document).keypress(function (e) {
                if (e.which != 8 && e.which != 46 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                    return false;
                }
            });
        },
        renderElement:function(){
            this._super();
            var self = this;
        	self.open_form();
        },
        open_form: function() {
        	var self = this;
            var open_table_row = "<tr id='open_balance_row'>" +
                            "<td><input type='text'  class='openbalance_td' id='value' value='0.00' /></td>" +
                            "<td><input type='text' class='openbalance_td' id='no_of_values' value='0.00' /></td>" +
                            "<td><input type='text' class='openbalance_td' id='subtotal' disabled='true' value='0.00' /></td>" +
                            "<td id='delete_row'><span class='fa fa-trash-o' style='font-size: 20px;'></span></td>" +
                            "</tr>";
            $('#opening_cash_table tbody').append(open_table_row);
            $('#add_open_balance').click(function(){
                $('#opening_cash_table tbody').append(open_table_row);
            });
            $('#opening_cash_table tbody').on('click', 'tr#open_balance_row td#delete_row',function(){
                $(this).parent().remove();
                self.compute_subtotal();
			});
            $('#opening_cash_table tbody').on('change focusout', 'tr#open_balance_row td',function(){
                var no_of_value, value;
                if($(this).children().attr('id') === "value"){
                    value = Number($(this).find('#value').val());
                    no_of_value = Number($(this).parent().find('td #no_of_values').val());
                }else if($(this).children().attr('id') === "no_of_values"){
                    no_of_value = Number($(this).find('#no_of_values').val());
                    value = Number($(this).parent().find('td #value').val());
                }
                $(this).parent().find('td #subtotal').val(value * no_of_value);
                self.compute_subtotal();
            });
            this.compute_subtotal = function(event){
                var subtotal = 0;
                _.each($('#open_balance_row td #subtotal'), function(input){
                    if(Number(input.value) && Number(input.value) > 0){
                        subtotal += Number(input.value);
                    }
                });
                $('.open_subtotal').text(self.format_currency(subtotal));
            }
            $('#validate_open_balance').click(function(){
                var items = []
                var open_balance = []
                var total_open_balance = 0.00;
                $(".openbalance_td").each(function(){
                    items.push($(this).val());
                });
                while (items.length > 0) {
                  open_balance.push(items.splice(0,3))
                }
                _.each(open_balance, function(balance){
                    total_open_balance += Number(balance[2])
                });
                if(total_open_balance > 0){
                	new Model('pos.session').call('open_balance',
                    [self.pos.pos_session.id,total_open_balance], {}, { async: false })
                    .then(function(res){
	                    if(res){
	                        self.gui.show_screen('products');
	                    }
                    }).fail(function (type, error){
                        if(error.code === 200 ){    // Business Logic Error, not a connection problem
                           self.gui.show_popup('error-traceback',{
                                'title': error.data.message,
                                'body':  error.data.debug
                           });
                        }
                    });
                } else{
                    return;
                }
            });
        },
    });
    gui.define_screen({name:'openingbalancescreen', widget: OpeningBalanceScreenWidget});
});