/**
 *
 **/
Ext._define('standard.ChoiceManage', {
    extend: 'toolkit.widget.TabPanel',

    getChoiceGrid: function(cfg) {
        if(!this._choiceGrid)
            this._choiceGrid = Ext._create('standard.ChoiceGrid', {
                region: 'center'
            });
            this._choiceGrid.setFilterProperty('active', true, 1011);

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
                    this.getChoiceGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        standard.ChoiceManage.superclass.constructor.call(this, cfg);
    }
});
