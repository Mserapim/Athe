Ext._define('raf.activity.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.activity.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Promotoria', dataIndex: 'workerlocation_unicode', id: 'autoExpandColumn'},
                    {header: 'Item', dataIndex: 'item_unicode', width: 90},
                    {header: 'Subitem', dataIndex: 'subitem_unicode', width: 90},
                    {header: 'Qtd Athenas', dataIndex: 'amount_athenas', width: 40},
                    {header: 'Qtd Submetido', dataIndex: 'amount_submitted', width:40},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.activity.Restful',
    'raf.activity.Grid'
);
