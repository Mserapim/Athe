Ext._define('corregedoria.cirdir.irscode.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.irscode.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Código', dataIndex: 'code', width: 100, },
                    {header: 'Desscrição', dataIndex: 'title', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.irscode.Restful',
    'corregedoria.cirdir.irscode.Grid'
);
