/**
 *
 **/
Ext._define('standard.configuration.item.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getChoiceGrid: function(cfg) {
        if(!this._grid)
            this._grid = Ext._create('standard.configuration.item.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Itens'
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
        standard.configuration.item.Manage.superclass.constructor.call(this, cfg);
    }
});
