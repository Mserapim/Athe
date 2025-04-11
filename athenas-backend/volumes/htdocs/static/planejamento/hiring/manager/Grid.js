Ext._define('planning.hiring.manager.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.manager.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'search'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Gestor', dataIndex: 'unicode', sortable: true, menuDisabled: true, id: 'autoExpandColumn'},
                    {header: 'Função', dataIndex: 'tipo_display', width: 300, sortable: true},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.manager.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.manager.Restful',
    'planning.hiring.manager.Grid'
);
