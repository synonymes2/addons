odoo.define('pos_session_z_report_omax', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var ActionManager = require('web.ActionManager');

    var QWeb = core.qweb;
    var ZSessionReportPrintButton = screens.ActionButtonWidget.extend({
        template: 'ZSessionReportPrintButton',
        button_click: function(){
            var self = this;
            var pos_session_id = self.pos.pos_session.id;
            self.pos.chrome.do_action(
                    'pos_session_z_report_omax.action_report_session_z', {
                        additional_context: {active_ids: [pos_session_id]},
                    });
        },
    });

    screens.define_action_button({
        'name': 'Z_session_report_print',
        'widget': ZSessionReportPrintButton,
        'condition': function(){ 
            return this.pos.config.omax_session_z_report;
        },
    });
});
