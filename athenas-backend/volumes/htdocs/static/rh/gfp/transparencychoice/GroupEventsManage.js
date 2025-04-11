/**
 *
 **/
Ext._define('rh.gfp.transparencychoice.GroupEventsManage', {
    extend: 'toolkit.widget.TabPanel',

    getChoiceGrid: function(cfg) {
        if(!this._choiceGrid)
            this._choiceGrid = Ext._create('rh.gfp.transparencychoice.GroupEventsGrid', {
                region: 'center',
                gridAutoLoad: false,
            });
            // this._choiceGrid.setFilter([
            //     {'property': 'app_label', 'value': 'gfp', 'stage': 0},
            //     {'property': 'name', 'value': 'CONFIG_TRANSPARENCY', 'stage': 1},
            //     {'property': 'name', 'value': 'GROUP_TRANSPARENCY', 'stage': 1},
            // ])

        return this._choiceGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor Portal Transparência'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getChoiceGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        rh.gfp.transparencychoice.GroupEventsManage.superclass.constructor.call(this, cfg);
    }
});
