/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.BaseConhecimento.Grid', {
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
                title: 'Base de Conhecimento'
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
        common.siatu.BaseConhecimento.Manager.superclass.constructor.call(this, cfg);
    }
});
