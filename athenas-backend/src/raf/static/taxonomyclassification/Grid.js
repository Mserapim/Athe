Ext._define('raf.taxonomyclassification.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.taxonomyclassification.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'CNMP', dataIndex: 'cnmp_code', width: 60},
                    {header: 'Classificação', dataIndex: 'title', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.taxonomyclassification.Restful',
    'raf.taxonomyclassification.Grid'
);
