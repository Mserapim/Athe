/**
 *
 **/
Ext._define('engine.TaskMessageManage', {
    extend: 'toolkit.widget.TabPanel',

    getTaskMessageGrid: function(cfg) {
        if(!this._TaskMessageGrid)
            this._TaskMessageGrid = Ext._create('engine.TaskMessageGrid', {
                region: 'center'
            });

        return this._TaskMessageGrid;
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
                    this.getTaskMessageGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        engine.TaskMessageManage.superclass.constructor.call(this, cfg);
    }
});
