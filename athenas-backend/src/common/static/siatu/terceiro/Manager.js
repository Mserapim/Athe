/**
 *
 **/
Ext._define('common.siatu.terceiro.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.terceiro.Grid', {
                region: 'center',
                // title:'Terceiro Interno',
            });
        }

         return this._Grid;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Terceiros'
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
        common.siatu.terceiro.Manager.superclass.constructor.call(this, cfg);
    }
});
