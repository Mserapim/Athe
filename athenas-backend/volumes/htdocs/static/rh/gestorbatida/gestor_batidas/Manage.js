Ext._define('rh.gestorbatida.gestor_batidas.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGestorBatidasGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('rh.gestorbatida.gestor_batidas.Grid', {
                region: 'center',
                gridAutoLoad: true,
                columnAction: false,
                doubleClickHandler: function () { }
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Batidas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGestorBatidasGrid(),
                ]
            }
        );

        rh.gestorbatida.gestor_batidas.Manage.superclass.constructor.call(this, cfg);
    }
});

