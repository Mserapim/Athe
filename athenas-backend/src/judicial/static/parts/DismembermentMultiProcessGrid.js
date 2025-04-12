
Ext._define('judicial.parts.DismembermentMultiProcessGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.parts.DismembermentMultiProcessWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Descricao', dataIndex: 'unicode', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.parts.DismembermentMultiProcessRestful',
    'judicial.parts.DismembermentMultiProcessGrid'
);
