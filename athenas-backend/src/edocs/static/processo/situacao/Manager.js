/**
 *
 **/
Ext._define('edocs.processo.situacao.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getSituacaoGrid: function(cfg) {
        if(!this._situacaoGrid)
             this._situacaoGrid = Ext._create('edocs.processo.situacao.Grid', {
                region: 'center',
            }); 

        return this._situacaoGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Situações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                         this.getSituacaoGrid()
                ]
            }
        );

        edocs.processo.situacao.Manager.superclass.constructor.call(this, cfg);
    }
});

