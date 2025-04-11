Ext._define('judicial.reports.BaseWindow', {
    extend: 'engine.mq.ReportWindow',

    controller: undefined,
    
    prepareValues: function(values) {
        var self = this;
        values = judicial.reports.BaseWindow.superclass.prepareValues.call(this, values);
        
        ['data_inicial', 'data_final'].forEach(
            function(attr) {
                if (values[attr]) 
                    values[attr] = self.prepareDate(values[attr])
            }
        );
        
        return values;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, { resizable: false });

        judicial.reports.BaseWindow.superclass.constructor.call(this, cfg);
    }
});