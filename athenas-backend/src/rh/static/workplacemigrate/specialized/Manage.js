Ext._define('rh.workplacemigrate.specialized.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function () {
        if (!this._grid)
            this._grid = Ext._create('rh.workplacemigrate.specialized.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Migração de Lotações/Órgãos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.workplacemigrate.specialized.Manage.superclass.constructor.call(this, cfg);
    }
});
