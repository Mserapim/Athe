Ext._define('rh.afastamento.afastamentorecessoforense.Manage', {
    extend: 'rh.afastamento.afastamento.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.afastamentorecessoforense.Grid', {
                region: 'center',
                // hideItemsToolbar: ['remove'],
                // hideActions: ['remove'],
                allowRemove: false
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};


        Ext.applyIf(
            cfg,
            {
               title: 'Afastamento Recesso Forense - Membros'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.afastamentorecessoforense.Manage.superclass.constructor.call(this, cfg);
    }
});
