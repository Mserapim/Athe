/**
 *
 **/
Ext._define('common.siatu.chamado.TabTransferencia', {
    extend: 'Ext.Panel',

    getTransferenciaGrid: function(cfg){
        if(!this._transfGrid){
            this._transfGrid = Ext._create('common.siatu.chamado.transferencia.Grid', Ext.applyIf({
                title:'Transferências do chamado',
                region: 'center',
                gridAutoLoad: false
                }, cfg)
            );
        }

        return this._transfGrid
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                title: 'Transferência',
                layout: 'border',
                items:[
                    this.getTransferenciaGrid(cfg),
                ]
            }


        );

        common.siatu.chamado.TabTransferencia.superclass.constructor.call(this, cfg);
    }

});