Ext._define('judicial.TagGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.TagWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Marcador', dataIndex: 'title', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.TagRestful',
    'judicial.TagGrid'
);

