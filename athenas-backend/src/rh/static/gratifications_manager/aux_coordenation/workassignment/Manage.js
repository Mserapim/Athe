/**
 *
 **/

 Ext._define('rh.gratifications_manager.aux_coordenation.workassignment.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.gratifications_manager.aux_coordenation.workassignment.Grid', {
                region: 'center',
            });
            this._grid.setParam('designacao', true);

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Designações de Exercício'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.gratifications_manager.aux_coordenation.workassignment.Manage.superclass.constructor.call(this, cfg);
    }
});
