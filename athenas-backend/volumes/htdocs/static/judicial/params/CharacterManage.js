/**
 *
 **/
Ext._define('judicial.params.CharacterManage', {
    extend: 'toolkit.widget.TabPanel',

    getCharacterGrid: function() {
        if(!this._characterGrid) {
            this._characterGrid = Ext._create('judicial.params.CharacterGrid', {
                region: 'center'
            });
        }

        return this._characterGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Personagens'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getCharacterGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.params.CharacterManage.superclass.constructor.call(this, cfg);
    }
});
