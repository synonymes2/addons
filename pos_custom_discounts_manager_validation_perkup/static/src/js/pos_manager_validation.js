odoo.define('pos_custom_discounts_manager_validation.pos_custom_discounts_manager_validation', function (require) {
"use strict";

var core = require('web.core');
var discounts = require('pos_custom_discounts.pos_custom_discounts');

var _t = core._t;


discounts.include({
    validateByManager: function() {
        var self = this;
        var managerUserIDs = this.pos.config.manager_user_ids;
        var users = this.pos.users;

        this.gui.show_popup('password', {
            'title': _t('Manager Validation'),
            confirm: function(password) {
                this.pos.manager = false;
                for (var i = 0; i < users.length; i++) {
                    if (managerUserIDs.indexOf(users[i].id) > -1
                            && password === (users[i].pos_security_pin || '')) {
                        this.pos.manager = users[i];
                    }
                }
                if (this.pos.manager) {
                    self.gui.show_popup('custom_discount', _t("Customize Discount"));
                } else {
                    self.gui.show_popup('error', _t('Incorrect Password'));
                    self.gui.current_screen.order_widget.numpad_state.reset();
                }
            },
        });
    },

    show: function() {
        var managerUserIDs = this.pos.config.manager_user_ids;
        var user = this.pos.manager || this.pos.get_cashier();

        if (this.pos.config.iface_validate_custom_discounts
                && managerUserIDs.indexOf(user.id) === -1) {
            this.validateByManager();
        } else {
            this._super();
            this.pos.manager = false;
        }
    },
});


});
