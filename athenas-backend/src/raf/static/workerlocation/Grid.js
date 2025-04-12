 Ext._define('raf.workerlocation.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.workerlocation.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Orgão', dataIndex: 'location_unicode', id: 'autoExpandColumn'},
                    {header: 'Raf', dataIndex: 'raf_unicode', width: 200}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.workerlocation.Restful',
    'raf.workerlocation.Grid'
);
