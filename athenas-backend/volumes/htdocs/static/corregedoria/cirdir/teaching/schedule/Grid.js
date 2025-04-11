Ext._define('corregedoria.cirdir.teaching.schedule.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.teaching.schedule.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Id', dataIndex: 'pk', width: 70, },
                    {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.teaching.schedule.Restful',
    'corregedoria.cirdir.teaching.schedule.Grid'
);
