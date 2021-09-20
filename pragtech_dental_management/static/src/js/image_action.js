odoo.define('pragtech_dental_management.image_action', function(require) {
	"use strict";
	var Widget = require('web.Widget');
	var AbstractAction = require('web.AbstractAction');
//	var Model = require('web.DataModel');
	var core = require('web.core');
	var img_val;
	var rpc = require('web.rpc');
	var ResultImageView = Widget.extend(AbstractAction.prototype,{
		template : "ResultImageView",

		get_image_vals : function(ids) {
			var $def = $.Deferred();

//			new Model('website').call('image_url_new', [ids, 'datas']).then(function(image_details) {
//				$def.resolve(image_details);
//
//			});
			 rpc.query({
	                model: 'website',
	                method: 'image_url_new',
	                args:  [ids, 'datas'],
	            })
	            .then(function(image_details){
	            	$def.resolve(image_details);
	            });
			return $def;
		},

		window_close : function() {
			var self = this;
			self.getParent().trigger_up('history_back');
//			this.trigger_up('history_back');
			self.destroy();
		},

		init : function(parent, options) {
			this._super(parent);
			options = options || {};
			var self = this;

			self.vals = options.params.values;
			img_val = options.params.values;

		},

		new_fun : function(pointer, img_ids) {
			var $def = $.Deferred();
			var flag = 0;
			var total_element = '';
			pointer.get_image_vals(img_ids).then(function(res) {
				var img_tag = '';
				for (var k = 0; k < res.length; k++) {
					if (flag == 0) {
						img_tag = img_tag + '<div class="item active"><div class="col-xs-2"><a href="#1"><img id = ' + k + ' class = "img_objs" src = "' + res[k] + '" style = "height:128px;width:128px"></a></div></div>';
						flag = 1;
					} else {
						img_tag = img_tag + '<div class="item"><div class="col-xs-2"><a href="#1"><img id = ' + k + ' class = "img_objs" src = "' + res[k] + '" style = "height:128px;width:128px"></a></div></div>';
					}

				}
				self.$('#my_div').append(img_tag);
				$def.resolve(self.$('#my_div'));

				$('#theCarousel').carousel({
					interval : false,
					wrap : false
				});
				var total_img = img_val['image'].length;
				self.$('.multi-item-carousel .item').each(function() {

					var next = $(this).next();
					if (!next.length) {
						
						next = $(this).siblings(':first');
					}
					next.children(':first-child').clone().appendTo($(this));
					if (total_img == 1) {
						 $def=false;
						 $("#left_img").hide();
						 $("#right_img").hide();
						return $def;
					}
					if (total_img == 2) {
						 $def=false;
						 $("#left_img").hide();
						 $("#right_img").hide();
						return $def;
					}
					if (total_img == 3) {
						next = next.next();
						if (!next.length) {
							next = $(this).siblings(':first');
						}
						next.children(':first-child').clone().appendTo($(this));
						$def=false;
						$("#left_img").hide();
						$("#right_img").hide();
						return $def;
					} else {
						for (var i = 0; i < 2; i++) {
							next = next.next();
							if (!next.length) {
								next = $(this).siblings(':first');
							}
							next.children(':first-child').clone().appendTo($(this));
						}
					}
				});
			});
			return $def;
		},
		execute_div : function(pointer) {
			var $def = $.Deferred();
			console.log("In img vals---------------",img_val)
			var img_vals = img_val;
			var flag = 0;
			var k;
			var img_ids = new Array();
			for (var j = 0; j < img_vals['image'].length; j++) {
				img_ids.push(img_vals['image'][j]);
			}
			pointer.new_fun(pointer, img_ids).then(function(res) {
				$def.resolve(res);
			});
			return $def
		},
		renderElement : function(parent, options) {
			this._super(parent);
			options = options || {};
			var self = this;
			self.execute_div(self).then(function(res) {
				$('.item').on('click', '.img_objs', function() {
					var src = this.src;
					$('#zoomed').empty();
					$('#zoomed').append('<img src = ' + src + ' width = "91%" height = "100%"/>');
				});
				$('#close_screen').click(function() {
					self.window_close();
				});
			});

		},
	});

	core.action_registry.add('result_images', ResultImageView);

	return {
		ResultImageView : ResultImageView
	};

});
