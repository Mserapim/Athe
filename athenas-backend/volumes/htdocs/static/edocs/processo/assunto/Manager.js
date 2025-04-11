/**
 *
 **/
Ext._define('edocs.processo.assunto.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getAssuntoGrid: function(cfg) {
        if(!this._assuntoGrid)
             this._assuntoGrid = Ext._create('edocs.processo.assunto.Grid', {
                region: 'center',
            }); 

        return this._assuntoGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Assuntos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                         this.getAssuntoGrid()
                ]
            }
        );

        edocs.processo.assunto.Manager.superclass.constructor.call(this, cfg);
    }
});

