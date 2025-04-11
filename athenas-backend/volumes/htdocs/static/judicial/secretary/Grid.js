Ext._define('judicial.secretary.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.secretary.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        judicial.secretary.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'judicial.secretary.Restful',
    'judicial.secretary.Grid'
);

