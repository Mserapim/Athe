Ext._define('adm.patrimonio.reports.BaseWindow', {
    extend: 'engine.mq.ReportWindow',

    controller: undefined,

    prepareValues: function(values) {
        values = adm.patrimonio.reports.BaseWindow.superclass.prepareValues.call(this, values);

        ['data_inicial', 'data_final'].forEach(
            function(attr) {
                if (values[attr])
                    values[attr] = this.prepareDate(values[attr]);
            }
        );

        return values;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, { resizable: false });

        adm.patrimonio.reports.BaseWindow.superclass.constructor.call(this, cfg);
    }
});
