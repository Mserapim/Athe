/**
 *
 **/
Ext._define('common.siatu.gerente.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGerenteGrid: function() {
        if(!this._gerenteGrid)
            this._gerenteGrid = Ext._create('common.siatu.gerente.Grid', {
                region: 'center',
                split: true,
                minWidth: 400,
                width:450,
                minHeight: 300,
            });

        return this._gerenteGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Gerentes'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                         this.getGerenteGrid(),
                ]
            }


        );

        common.siatu.gerente.Manager.superclass.constructor.call(this, cfg);
    }
});

