
Ext._define('rh.anotacao.tipodocumento.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function(args) {
        if(!this._grid)
            this._grid = Ext._create('rh.anotacao.tipodocumento.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Tipo de Documento(s)'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.anotacao.tipodocumento.Manage.superclass.constructor.call(this, cfg);
    }
});
