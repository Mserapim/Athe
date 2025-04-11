Ext._define('raf.activity.Launcher', {
    extend: 'toolkit.widget.TabPanel',

    getActivityGrid: function() {
        if(!this._activityGrid)
            this._activityGrid = Ext._create('raf.activity.Grid', {
                region: 'center',
            });

        return this._activityGrid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Atividades'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getActivityGrid()
            }
        );

        raf.activity.Launcher.superclass.constructor.call(this, cfg);
    }
});
