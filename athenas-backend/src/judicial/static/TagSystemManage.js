/**
 *
 **/
Ext._define('judicial.TagSystemManage', {
    extend: 'toolkit.widget.TabPanel',

    getChoiceGrid: function(cfg) {
        if(!this._choiceGrid) {
            this._choiceGrid = Ext._create('judicial.TagGrid', {
                region: 'center',
                params: {
                    tag_type: 1
                }
            });

            this._choiceGrid.setFilterProperty('tag_type', 1, 1011);
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
        judicial.TagSystemManage.superclass.constructor.call(this, cfg);
    }
});
