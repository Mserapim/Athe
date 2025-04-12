Ext._define('rh.anotacao.tipodocumento.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.anotacao.tipodocumento.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tipo de Documento', dataIndex: 'tipo', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.anotacao.tipodocumento.Restful',
    'rh.anotacao.tipodocumento.Grid'
);

