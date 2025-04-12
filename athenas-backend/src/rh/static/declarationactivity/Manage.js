/**
 *
 **/

Ext._define('rh.declarationactivity.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.declarationactivity.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Declaração de Atividade'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.declarationactivity.Manage.superclass.constructor.call(this, cfg);
    }
});
