/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.modelo.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.BaseConhecimento.modelo.Grid', {
                region: 'center',
            });
        }

         return this._Grid;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Modelo - Base de Conhecimento'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid(),
                ]
            }
        );
        common.siatu.BaseConhecimento.modelo.Manager.superclass.constructor.call(this, cfg);
    }
});
