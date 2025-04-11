/**
 *
 **/
Ext._define('judicial.params.judicialchoice.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getChoiceGrid: function(cfg) {
        if(!this._choiceGrid) {
            this._choiceGrid = Ext._create('judicial.params.judicialchoice.Grid', {
                region: 'center'
            });
            
            this._choiceGrid.setFilterProperty('active', true, 1011);
        }

        return this._choiceGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Opções'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getChoiceGrid(cfg)
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.params.judicialchoice.Manage.superclass.constructor.call(this, cfg);
    }
});
