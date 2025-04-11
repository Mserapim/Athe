/**
 *
 **/

Ext._define('rh.gratifications_manager.gratifications.workplace_tag.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.gratifications_manager.gratifications.workplace_tag.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Tags de Gratificação'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.gratifications_manager.gratifications.workplace_tag.Manage.superclass.constructor.call(this, cfg);
    }
});
