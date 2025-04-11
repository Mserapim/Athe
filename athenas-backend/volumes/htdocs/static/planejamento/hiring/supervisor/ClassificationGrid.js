Ext._define('planning.hiring.supervisor.ClassificationGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.supervisor.ClassificationWindow',

    // configOrderToolBar: ['add', 'edit', 'remove', '-', '->', '-'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Classificação', dataIndex: 'kind_display', id: 'autoExpandColumn', sortable: true},
                    {header: 'Ativo', dataIndex: 'active', sortable: true, renderer: function(value) {return (value ? 'SIM' : 'NÃO');}},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'planning.hiring.supervisor.ClassificationRestful',
    'planning.hiring.supervisor.ClassificationGrid'
);
