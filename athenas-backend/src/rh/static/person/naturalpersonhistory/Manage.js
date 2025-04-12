Ext._define('rh.person.naturalpersonhistory.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.person.naturalpersonhistory.Grid', {
                region: 'center',
                hideActions: ['remove'],
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Histórico de Pessoa Fisíca'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.person.naturalpersonhistory.Manage.superclass.constructor.call(this, cfg);
    }
});
