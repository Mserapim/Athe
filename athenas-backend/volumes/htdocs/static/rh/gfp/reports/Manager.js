Ext._define('rh.gfp.reports.Manager', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Reports',
        });

        Ext.apply(cfg, {
            layout: 'fit',
            items: Ext._create('rh.gfp.reports.Container'),
        });

        rh.gfp.reports.Manager.superclass.constructor.call(this, cfg);
    },
});
