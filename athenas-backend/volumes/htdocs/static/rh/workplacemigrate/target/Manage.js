Ext._define('rh.workplacemigrate.target.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function () {
        if (!this._grid)
            this._grid = Ext._create('rh.workplacemigrate.target.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Migração de lotações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.workplacemigrate.target.Manage.superclass.constructor.call(this, cfg);
    }
});
