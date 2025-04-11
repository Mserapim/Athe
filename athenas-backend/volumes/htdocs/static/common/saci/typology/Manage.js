/**
 *
 **/
Ext._define('common.saci.typology.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getTypologyGrid: function(cfg) {
        if(!this._typologyGrid)
            this._typologyGrid = Ext._create('common.saci.typology.Grid', {
                region: 'center'
            });

        return this._typologyGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Tipologia de Público'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getTypologyGrid()
                ]
            }
        );

        common.saci.typology.Manage.superclass.constructor.call(this, cfg);
    }
});
