/**
 *
 **/
Ext._define('common.siatu.chamado.TabAnexo', {
    extend: 'Ext.Panel',

    getGrid: function(){
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.chamado.anexo.Grid',{
                title:'Anexos',
                region: 'center',
                }
            );
        }

        return this._Grid
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
            	title: 'Anexos',
                layout: 'border',
                items:[
                    this.getGrid(),
                ]
            }


        );

        common.siatu.chamado.TabAnexo.superclass.constructor.call(this, cfg);
    }

});