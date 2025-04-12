Ext._define('planning.hiring.document.DocumentManager', {
    extend: 'toolkit.widget.TabPanel',

    documentGrid: function() {
        if(!this._documentGrid) {
            this._documentGrid = Ext._create('planning.hiring.document.DocumentGrid', {
                title: 'Documentos',
                region: 'center',
                // height: 300,
                gridAutoLoad: true
            });
        }

        return this._documentGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});[]

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Arquivos',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.documentGrid()
                ]
            }
        );

        planning.hiring.document.DocumentManager.superclass.constructor.call(this, cfg);
    }
});
