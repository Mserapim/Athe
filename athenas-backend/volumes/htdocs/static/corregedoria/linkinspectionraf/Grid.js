Ext._define('corregedoria.linkinspectionraf.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.linkinspectionraf.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tabela da Inspeção', dataIndex: 'inspection_table_display', width: 200, },
                    {header: 'Questionário', dataIndex: 'raf_quiz', width: 325, },
                    {header: 'Item', dataIndex: 'raf_item_unicode', width: 325, },
                    {header: 'Subitem', dataIndex: 'raf_subitem_unicode', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.linkinspectionraf.Restful',
    'corregedoria.linkinspectionraf.Grid'
);
