Ext._define('raf.typequiz.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.typequiz.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Grupo', dataIndex: 'group_display', width: 125},
                    {header: 'Espécie', dataIndex: 'species_display', width: 125},
                    {header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.typequiz.Restful',
    'raf.typequiz.Grid'
);
