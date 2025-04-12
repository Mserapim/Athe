/**
 *
 **/
Ext._define('apd.periodicevaluationperformance.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getAPD: function() {
        if(!this.apd) {
            this.apd = Ext._create('apd.periodicevaluationperformance.PeriodicEvaluationPerformanceGrid', {
                region: 'center',
            });
        }

        return this.apd;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de APD'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getAPD(),
                ]
            }
        );

        apd.periodicevaluationperformance.Manage.superclass.constructor.call(this, cfg);
    }
});
