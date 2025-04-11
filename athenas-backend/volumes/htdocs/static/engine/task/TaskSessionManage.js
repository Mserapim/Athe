/**
 *
 **/
Ext._define('engine.TaskSessionManage', {
    extend: 'toolkit.widget.TabPanel',

    getTaskSessionGrid: function(cfg) {
        if(!this._TaskSessionGrid)
            this._TaskSessionGrid = Ext._create('engine.TaskSessionGrid', {
                region: 'center'
            });

        return this._TaskSessionGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Tarefas Executadas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getTaskSessionGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        engine.TaskSessionManage.superclass.constructor.call(this, cfg);
    }
});
