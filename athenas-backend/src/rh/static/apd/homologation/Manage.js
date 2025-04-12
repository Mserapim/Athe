/**
 *
 **/
Ext._define('apd.homologation.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getAPD: function() {
        if(!this.apd) {
            this.apd = Ext._create('apd.periodicevaluationperformance.PeriodicEvaluationPerformanceGrid', {
                region: 'center',
                gridAutoLoad: false,
                configOrderToolBar: ['openManager', 'search', '-',  '->'],
            });
        }

        var tbar = this.apd.getToolbar();

        tbar.getComponent(0).menu.items.get('repetir_avaliacao').hide();
        tbar.remove(7);
        // this.apd.addFilterProperty('status', 1, 100, false);
        this.apd.addFilterProperty('evaluation_apd__resource_apd__decision__in', [1,2], 100, false);
        this.apd.addFilterProperty('manifestation_apd__isnull', false, 101, true);

        return this.apd;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Homologação de APD'
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

        apd.homologation.Manage.superclass.constructor.call(this, cfg);
    }
});